"""Measure footprint, latency and throughput on the deployment target.

One script rather than three: on a board reached over SSH, every extra command
is an occasion to mistype something, and the three measurements belong in one
file anyway.

Run: ./.venv/bin/python scripts/measure_pi.py --label "raspberry-pi-4"
"""

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import MODELS_DIR, ROOT  # noqa: E402
from src.inference import Predictor  # noqa: E402

WARMUP, RUNS = 10, 200
BATCHES = [1, 10, 100, 1000]


def configuration(label: str) -> dict:
    """Everything needed to read the timings that follow.

    Milliseconds mean nothing without the machine that produced them, and this
    is the one detail nobody remembers to write down afterwards.
    """
    def lire(commande, defaut="inconnu"):
        try:
            return subprocess.check_output(commande, shell=True,
                                           text=True).strip()
        except Exception:  # noqa: BLE001
            return defaut

    return {
        "label": label,
        "machine": platform.machine(),
        "processeur": lire(
            "lscpu | grep 'Model name' | cut -d: -f2 | xargs"),
        "coeurs": lire("nproc"),
        "frequence_max_mhz": lire(
            "lscpu | grep 'CPU max MHz' | cut -d: -f2 | xargs"),
        "memoire_totale": lire(
            "awk '/MemTotal/ {printf \"%.1f GiB\", $2/1024/1024}' /proc/meminfo"),
        "systeme": lire(
            "grep PRETTY_NAME /etc/os-release | cut -d'\"' -f2"),
        "noyau": platform.release(),
        "python": platform.python_version(),
    }


def empreinte(predictor) -> dict:
    """Model size and resident memory, at rest and under load."""
    import resource

    fichiers = {p.name: p.stat().st_size
                for p in MODELS_DIR.glob("*")
                if p.is_file() and p.suffix in (".joblib", ".keras")}

    au_repos = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    rng = np.random.default_rng(0)
    lot = pd.DataFrame(rng.random((1000, len(predictor.raw_columns))),
                       columns=predictor.raw_columns)
    predictor.predict_proba(lot)
    en_charge = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    return {
        "modele_final_ko": round(
            fichiers.get(
                predictor.name.replace(" ", "_") + ".joblib", 0) / 1024, 1),
        "tous_modeles_ko": round(sum(fichiers.values()) / 1024, 1),
        # ru_maxrss is in kilobytes on Linux, bytes on macOS.
        "memoire_au_repos_mo": round(au_repos / 1024, 1),
        "memoire_en_charge_mo": round(en_charge / 1024, 1),
    }


def latence(predictor) -> dict:
    """Single-vehicle latency, warm-up excluded.

    The first calls carry lazy imports and memory allocation, and on a board
    they can take a hundred times longer than the rest. Including them would
    suggest the requirement is at risk when it is not.
    """
    vide = pd.DataFrame([{c: np.nan for c in predictor.raw_columns}])

    for _ in range(WARMUP):
        predictor.predict_proba(vide)

    mesures = []
    for _ in range(RUNS):
        debut = time.perf_counter()
        predictor.predict_proba(vide)
        mesures.append((time.perf_counter() - debut) * 1000)

    mesures = np.array(mesures)
    pd.DataFrame({"latency_ms": mesures}).to_csv(
        ROOT / "reports" / "latency_pi_single.csv", index=False)

    return {
        "n": len(mesures),
        "mediane_ms": round(float(np.median(mesures)), 2),
        "neuvieme_decile_ms": round(float(np.percentile(mesures, 90)), 2),
        "95e_centile_ms": round(float(np.percentile(mesures, 95)), 2),
        # The worst case matters more here than anywhere else in this project:
        # it is what decides whether a deadline could be met at all.
        "maximum_ms": round(float(mesures.max()), 2),
        "ecart_type_ms": round(float(mesures.std()), 2),
    }


def debit(predictor) -> dict:
    """Throughput by batch size, and the ceiling a single process sustains."""
    rng = np.random.default_rng(1)
    lignes = []
    for taille in BATCHES:
        lot = pd.DataFrame(rng.random((taille, len(predictor.raw_columns))),
                           columns=predictor.raw_columns)
        predictor.predict_proba(lot)          # warm-up for this size
        debut = time.perf_counter()
        predictor.predict_proba(lot)
        ecoule = (time.perf_counter() - debut) * 1000
        lignes.append({
            "taille_lot": taille,
            "total_ms": round(ecoule, 1),
            "par_vehicule_ms": round(ecoule / taille, 3),
        })

    table = pd.DataFrame(lignes)
    table.to_csv(ROOT / "reports" / "throughput_pi.csv", index=False)

    # Two ceilings, and confusing them overstates the system by a factor of
    # five hundred. The service answers one vehicle per request, so its ceiling
    # is the inverse of the single-vehicle latency. The batch figure describes
    # a different job: scoring a fleet from a file in one go, where the fixed
    # cost is amortised over a thousand rows.
    unitaire = table.loc[table["taille_lot"] == 1, "par_vehicule_ms"].iloc[0]
    par_lot = table["par_vehicule_ms"].min()

    return {
        "par_lot": lignes,
        "plafond_unitaire_par_seconde": round(1000 / unitaire, 1),
        "plafond_par_lot_par_seconde": round(1000 / par_lot, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="raspberry-pi-4")
    args = parser.parse_args()

    predictor = Predictor.load()

    print("=================== configuration")
    config = configuration(args.label)
    for cle, valeur in config.items():
        print(f"  {cle:<20} {valeur}")

    print("\n=================== empreinte")
    emp = empreinte(predictor)
    for cle, valeur in emp.items():
        print(f"  {cle:<24} {valeur}")

    print("\n=================== latence unitaire")
    lat = latence(predictor)
    for cle, valeur in lat.items():
        print(f"  {cle:<24} {valeur}")

    print("\n=================== débit par taille de lot")
    deb = debit(predictor)
    print(f"  {'lot':>6} {'total ms':>10} {'par véhicule ms':>18}")
    for ligne in deb["par_lot"]:
        print(f"  {ligne['taille_lot']:>6} {ligne['total_ms']:>10.1f} "
              f"{ligne['par_vehicule_ms']:>18.3f}")
              
              
    print(f"\n  plafond, un véhicule par requête : "
          f"{deb['plafond_unitaire_par_seconde']} par seconde")
    print(f"  plafond, notation d'une flotte   : "
          f"{deb['plafond_par_lot_par_seconde']} par seconde")

    resultat = {"configuration": config, "empreinte": emp,
                "latence": lat, "debit": deb}
    with open(ROOT / "reports" / f"deployment_{args.label}.json", "w",
              encoding="utf-8") as handle:
        json.dump(resultat, handle, indent=2, ensure_ascii=False)

    print(f"\nécrit dans reports/deployment_{args.label}.json")


if __name__ == "__main__":
    main()
