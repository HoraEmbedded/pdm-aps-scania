# Journal de bord

Une entree par seance de travail. Ce journal alimente directement le rapport
final : les difficultes notees a chaud sont impossibles a reconstituer en S10.

## Semaine 1

### Seance du 20/08/2026
- Fait : Mise en place de l'environnement de travail et téléchargement des données
- Difficulte rencontree : j'ai eu du mal à connecter l'environnement git et l'environnement .venv aussi. En effet, certaines commandes ne marchaient et après mes recherches j'ai appris que c'est à cause de la version de python (3.14) qui eest très récente et n'a encore bien mûris . j'ai donc installé la version 3.12 qui est l'intermédiaire parfait pour les deux
- Decision prise et justification :
- Prochaine action : On passe à la mission suivante

### Empreintes des donnees brutes
| Fichier | SHA256 | Date de telechargement |
|---------|--------|------------------------|
| aps_failure_training_set.csv | | |
| aps_failure_test_set.csv | | |


mkdir -p build
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -std=c11 -Og -g3 -ffreestanding -fno-common -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wshadow -Wconversion -Iinc -c src/main.c -o build/main.o
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -std=c11 -Og -g3 -ffreestanding -fno-common -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wshadow -Wconversion -Iinc -c src/startup.c -o build/startup.o
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -Tlinker/stm32f407.ld -nostdlib -Wl,--gc-sections -Wl,-Map=build/node-fw.map -Wl,--print-memory-usage build/main.o build/startup.o -o build/node-fw.elf
Memory region         Used Size  Region Size  %age Used
           FLASH:         300 B         1 MB      0.03%
             RAM:          1 KB       128 KB      0.78%
             CCM:           0 B        64 KB      0.00%
arm-none-eabi-size build/node-fw.elf
   text	   data	    bss	    dec	    hex	filename
    300	      0	   1024	   1324	    52c	build/node-fw.elf
arm-none-eabi-objcopy -O binary build/node-fw.elf build/node-fw.bin



uild/node-fw.elf:     file format elf32-littlearm

Contents of section .isr_vector:
 8000000 00000220 cd000008 c9000008 c9000008  ... ............
 8000010 c9000008 c9000008 c9000008 00000000  ................


gdb-multiarch -x tools/gdb/.gdbinit-renode node-fw/build/node-fw.elf
GNU gdb (Ubuntu 17.1-2ubuntu1) 17.1
Copyright (C) 2025 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from node-fw/build/node-fw.elf...
The target architecture is set to "arm".
Reset_Handler () at src/startup.c:16
16	{
(gdb) break main
Breakpoint 1 at 0x800006c: file src/main.c, line 31.
(gdb) continue
Continuing.

Breakpoint 1, main () at src/main.c:31
31	{
(gdb) next
33	    RCC_AHB1ENR |= (1u << 0);    /* GPIOAEN  */
(gdb) next
34	    RCC_APB1ENR |= (1u << 17);   /* USART2EN */
(gdb) print/x *(uint32_t*)0x40023830
$1 = 0x1
(gdb) next
40	    GPIOA_MODER = (GPIOA_MODER & ~(3u << 4)) | (2u << 4);
(gdb) print/x *(uint32_t*)0x40023840
$2 = 0x20000
(gdb) regs
RCC_AHB1ENR = 0x00000001
RCC_APB1ENR = 0x00020000
GPIOA_MODER = 0xA8000000
USART2_CR1  = 0x00000000
USART2_SR   = 0x000000C0
(gdb) info registers
r0             0x0                 0
r1             0x20000000          536870912
r2             0x20000             131072
r3             0x40023000          1073885184
r4             0x0                 0
r5             0x0                 0
r6             0x0                 0
r7             0x0                 0
r8             0x0                 0
r9             0x0                 0
r10            0x0                 0
r11            0x0                 0
r12            0x0                 0
sp             0x2001fff0          0x2001fff0
lr             0x80000f7           134217975
pc             0x8000088           0x8000088 <main+28>
xpsr           0x61000000          1627389952
msp            0x0                 0
psp            0x0                 0
primask        0x0                 0
basepri        0x0                 0
faultmask      0x0                 0
control        0x0                 0
(gdb) backtrace
#0  main () at src/main.c:40
(gdb) 



(100.899607)  vcan0  400   [8]  35 4C A0 26 78 CA 5E 64
 (100.901673)  vcan0  400   [8]  76 13 DD 37 2E E1 99 1D
 (100.903736)  vcan0  400   [8]  54 3C 2D 59 DA 51 2C 76
 (100.905800)  vcan0  400   [8]  B2 AA F1 77 E0 72 FA 0C
 (100.907865)  vcan0  400   [8]  64 85 B2 4C EC DB 13 70
 (100.909930)  vcan0  400   [8]  F8 B8 FA 00 F9 24 E7 51
 (100.911993)  vcan0  400   [8]  B5 01 EB 0F 28 82 BE 70
 (100.914058)  vcan0  400   [8]  83 25 76 36 29 A7 C8 78
 (100.916122)  vcan0  400   [8]  5D 69 18 2A 13 32 FF 11
 (100.918185)  vcan0  400   [8]  3D 89 F7 5C F4 F9 63 2A
 (100.920252)  vcan0  400   [8]  A4 2D 04 1A 77 37 9B 28
 (100.922317)  vcan0  400   [8]  18 72 71 70 30 43 14 62
 (100.924385)  vcan0  400   [8]  88 39 F7 03 12 25 68 74
 (100.926451)  vcan0  400   [8]  EC EE 0E 39 13 39 BC 60
 (100.928520)  vcan0  400   [8]  D7 D6 D3 4A 27 93 29 2B
 (100.930585)  vcan0  400   [8]  84 F6 21 33 0C 23 74 71
 (100.932651)  vcan0  400   [8]  9F 5D 88 0F FB 09 FF 6A
 (100.934720)  vcan0  400   [8]  3A 04 0E 0F F4 99 B5 68
 (100.936783)  vcan0  400   [8]  D5 5B 2B 61 EC AE FF 06
 (100.938850)  vcan0  400   [8]  D4 0C B0 75 3A E1 DD 2D
 (100.940915)  vcan0  400   [8]  D8 8A 13 77 CC C5 AA 76
 (100.942980)  vcan0  400   [8]  33 06 C5 7F 8D 8C FE 06
 (100.945047)  vcan0  400   [8]  F5 47 69 67 B7 2B 3B 36
 (100.947112)  vcan0  400   [8]  B6 33 C7 7F 52 B1 81 11
 (100.949175)  vcan0  400   [8]  CA 5D 3A 48 F3 BC BE 5C
 (100.951239)  vcan0  400   [8]  46 AB E5 3B 6E 8B 3E 62
 (100.953305)  vcan0  400   [8]  6B F4 59 05 5E 1D 57 2C
 (100.955371)  vcan0  400   [8]  9E CE 52 44 F3 2D 51 09
 (100.957436)  vcan0  400   [8]  70 42 BF 20 8A BD 61 7D
 (100.959500)  vcan0  400   [8]  06 67 0D 6A 47 19 93 6B
 (100.961567)  vcan0  400   [8]  B1 50 8B 28 8A 5D 2F 1D
 (100.963633)  vcan0  400   [8]  53 3C 07 5D 51 AE 13 38
 (100.965670)  vcan0  400   [8]  85 67 2E 08 8D 40 15 6C
 (100.967734)  vcan0  400   [8]  45 48 C9 20 5B C3 59 69
 (100.969797)  vcan0  400   [8]  79 EF 14 73 19 55 79 16
 (100.971862)  vcan0  400   [8]  95 A4 37 17 51 7A 28 6A
 (100.973924)  vcan0  400   [8]  E6 1A 24 0D C8 AA FC 16
 (100.975987)  vcan0  400   [8]  DE 06 27 71 DB 62 8D 74
 (100.978055)  vcan0  400   [8]  7F D6 37 4D 95 3A EE 70
 (100.980121)  vcan0  400   [8]  2D 14 0F 06 4A 34 72 15
 (100.982185)  vcan0  400   [8]  88 F7 AC 4D 73 BF F4 41
 (100.984248)  vcan0  400   [8]  B8 BF B0 77 F3 EB 06 53
 (100.986312)  vcan0  400   [8]  D2 DC 4B 6E 57 8E 03 3C
 (100.988378)  vcan0  400   [8]  E6 19 58 5C 42 1F 0B 0F
 (100.990441)  vcan0  400   [8]  E1 4B 65 39 EC 80 65 46
 (100.992505)  vcan0  400   [8]  8A 38 9E 7A 93 9C F0 61
 (100.994570)  vcan0  400   [8]  77 DE 94 63 DD 74 A5 57
 (100.996634)  vcan0  400   [8]  E4 4A 04 1A FC 45 C3 6B
 (100.998697)  vcan0  400   [8]  6B B5 BA 43 29 93 CD 3A
 (101.000760)  vcan0  400   [8]  57 09 1D 55 E4 A4 CF 36
 (101.002819)  vcan0  400   [8]  42 E8 46 51 EC AD 54 6C
 (101.004880)  vcan0  400   [8]  36 1F F8 20 28 03 6B 5E
 (101.006946)  vcan0  400   [8]  B5 58 51 03 14 26 1F 12
 (101.009011)  vcan0  400   [8]  03 66 F8 52 34 2F 89 50
 (101.011074)  vcan0  400   [8]  A9 60 0D 03 30 7A 07 59
 (101.013137)  vcan0  400   [8]  7E 63 FB 65 32 58 BA 50
 (101.015200)  vcan0  400   [8]  A4 39 FC 1A 37 23 AC 5D
 (101.017263)  vcan0  400   [8]  25 44 C1 23 76 16 48 09
 (101.019330)  vcan0  400   [8]  8E B1 AF 19 0C 5E 19 00
 (101.021395)  vcan0  400   [8]  B8 35 53 18 6F FD 14 53
 (101.023457)  vcan0  400   [8]  F8 DE 7E 46 42 6E F1 12
 (101.025523)  vcan0  400   [8]  02 9A 05 35 6F BD 13 2A
 (101.027588)  vcan0  400   [8]  20 E3 96 6A E6 E4 09 4F
 (101.029653)  vcan0  400   [8]  6C 03 D7 15 8B 98 51 2E
 (101.031802)  vcan0  400   [8]  0F 78 D7 09 C3 0C F4 6A
 (101.033889)  vcan0  400   [8]  6F 3D 21 65 52 60 1E 5B
 (101.037989)  vcan0  400   [8]  B0 BA 48 57 A5 5C 19 06
 (101.040069)  vcan0  400   [8]  7A 63 89 39 65 13 9A 5A
 (101.042140)  vcan0  400   [8]  BA 82 38 18 7E C9 81 0C
 (101.044204)  vcan0  400   [8]  99 42 23 2B 63 E3 45 1B
 (101.046272)  vcan0  400   [8]  AE 43 89 65 18 A6 1E 11
 (101.048344)  vcan0  400   [8]  95 3B 00 6C 52 7D 85 00
 (101.050411)  vcan0  400   [8]  4F C9 CA 6E BB 7F C1 0F
 (101.052438)  vcan0  400   [8]  C8 93 CD 09 DD 7A 7A 08
 (101.054508)  vcan0  400   [8]  C7 DD DA 0F 81 C9 20 22
 (101.056578)  vcan0  400   [8]  4C 78 8F 5B BF BC 59 56
 (101.058644)  vcan0  400   [8]  C3 37 12 35 4F 12 95 10
 (101.060673)  vcan0  400   [8]  2F 7A 6D 00 E3 1A A9 1F
 (101.062737)  vcan0  400   [8]  35 F7 9E 5F 9B 7D 44 16
 (101.064794)  vcan0  400   [8]  6E B3 FA 4D 45 6F 76 69
 (101.066850)  vcan0  400   [8]  5E 8A 38 01 DE F0 1B 33
 (101.068922)  vcan0  400   [8]  97 CF 94 44 0E 45 81 58
 (101.070992)  vcan0  400   [8]  83 4D 35 39 11 33 1E 7E
 (101.073062)  vcan0  400   [8]  73 58 1B 33 3D D0 6D 51
 (101.075132)  vcan0  400   [8]  8F FC 9F 0A 0D 9B 3E 5E
 (101.077198)  vcan0  400   [8]  A1 B3 B3 6C 3E 40 29 70
 (101.079262)  vcan0  400   [8]  25 41 5D 6F 36 EF B3 58
 (101.081327)  vcan0  400   [8]  90 BD AE 70 74 0A 28 5E
 (101.083392)  vcan0  400   [8]  F1 6E 75 68 59 51 7C 7A
 (101.085455)  vcan0  400   [8]  51 85 A2 66 B8 4C 50 78
 (101.087519)  vcan0  400   [8]  DA 1A 9D 1C 9D FD 31 42
 (101.089582)  vcan0  400   [8]  78 09 AA 4E 9D 52 AF 51
 (101.091647)  vcan0  400   [8]  EC 0F C7 52 A7 83 17 4F
 (101.093670)  vcan0  400   [8]  81 6D 58 71 22 07 66 32
 (101.095730)  vcan0  400   [8]  42 01 5C 65 EF 20 53 3F
 (101.097795)  vcan0  400   [8]  67 76 DC 1B A0 8B 94 66
 (101.099855)  vcan0  400   [8]  CD 11 6F 72 FE 45 71 60
 (101.101921)  vcan0  400   [8]  AF D0 15 3F 51 5F A4 2B
 (101.104059)  vcan0  400   [8]  0F 79 8F 5E 22 29 31 72
 (101.106120)  vcan0  400   [8]  8E 2F 12 7D 9F 75 2F 69



canplayer -I candump-*.log 
'=' missing in assignment!
canplayer - replay a compact CAN frame logfile to CAN devices.

Usage: canplayer <options> [interface assignment]*

Options:
         -I <infile>  (default stdin)
         -l <num>     (process input file <num> times)
                      (Use 'i' for infinite loop - default: 1)
         -t           (ignore timestamps: send frames immediately)
         -i           (interactive - wait for ENTER key to process next frame)
         -n <count>   (terminate after processing <count> CAN frames)
         -g <ms>      (gap in milli seconds - default: 1 ms)
         -s <s>       (skip gaps in timestamps > 's' seconds)
         -x           (disable local loopback of sent CAN frames)
         -v           (verbose: print sent CAN frames)

Interface assignment:
 0..n assignments like <write-if>=<log-if>

 e.g. vcan2=can0  (send frames received from can0 on vcan2)
 extra hook: stdout=can0  (print logfile line marked with can0 on stdout)
 No assignments  => send frames to the interface(s) they had been received from

Lines in the logfile not beginning with '(' (start of timestamp) are ignored.


mosquitto_sub -h localhost -p 1883 -t 'snt/#' -v
Error: Connection refused
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ cd ..
lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ sudo apt install -y mosquitto
[sudo: authenticate] Password:              
Installing:                     
  mosquitto

Installing dependencies:
  libdlt3  libwebsockets19t64

Summary:
  Upgrading: 0, Installing: 3, Removing: 0, Not Upgrading: 10
  Download size: 660 kB
  Space needed: 1,885 kB / 196 GB available

Get:1 http://ma.archive.ubuntu.com/ubuntu resolute/universe amd64 libdlt3 amd64 3.0.0-4 [193 kB]
Get:2 http://ma.archive.ubuntu.com/ubuntu resolute/universe amd64 libwebsockets19t64 amd64 4.3.5-3ubuntu1 [227 kB]
Get:3 http://ma.archive.ubuntu.com/ubuntu resolute/universe amd64 mosquitto amd64 2.0.22-5build1 [240 kB]
Fetched 660 kB in 10s (62.9 kB/s)  
Selecting previously unselected package libdlt3:amd64.
(Reading database… 212903 files and directories currently installed.)
Preparing to unpack …/libdlt3_3.0.0-4_amd64.deb…
Unpacking libdlt3:amd64 (3.0.0-4)…
Selecting previously unselected package libwebsockets19t64:amd64.
Preparing to unpack …/libwebsockets19t64_4.3.5-3ubuntu1_amd64.deb…
Unpacking libwebsockets19t64:amd64 (4.3.5-3ubuntu1)…
Selecting previously unselected package mosquitto.
Preparing to unpack …/mosquitto_2.0.22-5build1_amd64.deb…
Unpacking mosquitto (2.0.22-5build1)…
Setting up libwebsockets19t64:amd64 (4.3.5-3ubuntu1)…
Setting up libdlt3:amd64 (3.0.0-4)…
Setting up mosquitto (2.0.22-5build1)…
Created symlink '/etc/systemd/system/multi-user.target.wants/mosquitto.service' 
→ '/usr/lib/systemd/system/mosquitto.service'.
Processing triggers for man-db (2.13.1-1build1)…
Processing triggers for libc-bin (2.43-2ubuntu2.3)…
lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ sudo systemctl enable --now mosquitto
Synchronizing state of mosquitto.service with SysV service script with /usr/lib/systemd/systemd-sysv-install.
Executing: /usr/lib/systemd/systemd-sysv-install enable mosquitto


docker compose config --quiet && echo "YAML valide"
YAML valide
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ docker compose up -d
[+] up 38/39
 ✔ Image influxdb:2.7               Pulled                                367.1s
 ✔ Image eclipse-mosquitto:2.0      Pulled                                129.1s
 ✔ Image grafana/grafana:11.1.0     Pulled                                281.1s
 ✔ Network sentinelle_snt           Created                                 0.0s
 ✔ Volume sentinelle_influx_data    Created                                 0.0s
 ✔ Volume sentinelle_mosquitto_log  Created                                 0.0s
 ✔ Volume sentinelle_influx_cfg     Created                                 0.0s
 ✔ Volume sentinelle_grafana_data   Created                                 0.0s
 ✔ Volume sentinelle_mosquitto_data Created                                 0.0s
 ⠴ Container snt-mosquitto          Starting                                0.5s
 ✔ Container snt-influxdb           Started                                 0.4s
 ✔ Container snt-grafana            Started                                 0.3s
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint snt-mosquitto (600b761d912208cdf32f83f7f4b162a6bb37cc4772533bd66e629f5faf532d75): failed to bind host port 0.0.0.0:1883/tcp: address already in use
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ # 1. Stopper et désactiver le Mosquitto natif de la machine
sudo systemctl stop mosquitto
sudo systemctl disable mosquitto

# 2. Relancer votre conteneur Docker Compose
docker compose up -d
[sudo: authenticate] Password:              
sudo: Authentication failed, try again.
[sudo: authenticate] Password:              
Synchronizing state of mosquitto.service with SysV service script with /usr/lib/systemd/systemd-sysv-install.
Executing: /usr/lib/systemd/systemd-sysv-install disable mosquitto
Removed '/etc/systemd/system/multi-user.target.wants/mosquitto.service'.
[+] up 3/3
 ✔ Container snt-influxdb  Running                                          0.0s
 ✔ Container snt-grafana   Running                                          0.0s
 ✔ Container snt-mosquitto Started                                          0.1s
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ mosquitto_sub -h localhost -p 1883 -t 'snt/#' -v
Error: Connection refused
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ docker compose ps
NAME            IMAGE                    COMMAND                  SERVICE     CREATED         STATUS              PORTS
snt-grafana     grafana/grafana:11.1.0   "/run.sh"                grafana     3 minutes ago   Up 3 minutes        0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
snt-influxdb    influxdb:2.7             "/entrypoint.sh infl…"   influxdb    3 minutes ago   Up 3 minutes        0.0.0.0:8086->8086/tcp, [::]:8086->8086/tcp
snt-mosquitto   eclipse-mosquitto:2.0    "/docker-entrypoint.…"   mosquitto   3 minutes ago   Up About a minute   
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ mosquitto_sub -h localhost -p 1883 -t 'snt/#' -v
Error: Connection refused
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ docker compose down
docker compose up -d
[+] down 4/4
 ✔ Container snt-mosquitto Removed                                          0.1s
 ✔ Container snt-grafana   Removed                                          0.1s
 ✔ Container snt-influxdb  Removed                                          0.1s
 ✔ Network sentinelle_snt  Removed                                          0.1s
[+] up 4/4
 ✔ Network sentinelle_snt  Created                                          0.0s
 ✔ Container snt-influxdb  Started                                          0.2s
 ✔ Container snt-mosquitto Started                                          0.2s
 ✔ Container snt-grafana   Started                                          0.3s
lady_horacia@DESKTOP2Hora:~/dev/sentinelle/infra$ mosquitto_sub -h localhost -p 1883 -t 'snt/#' -v

mosquitto_sub -h localhost -p 1883 -t 'snt/#' -v
snt/v1/test hello sentinelle
snt/v1/node/1/features {"rms":0.42,"crest":3.1,"kurtosis":2.9}

{"name":"influxdb", "message":"ready for queries and writes", "status":"pass", "checks":[], "version": "v2.7.12", "commit": "ec9dcde5d6"}

grafana HTTP 200



python3 -m venv ~dev/sentinelle/.venvsource ~/sentinelle/.venv/bin/activate
pip install numpy scipy matplotlib
python3 plot_rc.py
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.14/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
python3: can't open file '/home/lady_horacia/dev/sentinelle/plot_rc.py': [Errno 2] No such file or directory
lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ python3 -m venv ~dev/sentinelle/.venvsource ~dev//sentinelle/.venv/bin/activate
lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ pip install numpy scipy matplotlib
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.14/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ python3 -m venv .venv
lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ source .venv/bin/activate
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ pip install numpy scipy matplotlib
Collecting numpy
  Downloading numpy-2.5.2-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (6.6 kB)
Collecting scipy
  Downloading scipy-1.18.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (62 kB)
Collecting matplotlib
  Downloading matplotlib-3.11.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (80 kB)
Collecting contourpy>=1.0.1 (from matplotlib)
  Downloading contourpy-1.3.3-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (5.5 kB)
Collecting cycler>=0.10 (from matplotlib)
  Using cached cycler-0.12.1-py3-none-any.whl.metadata (3.8 kB)
Collecting fonttools>=4.28.2 (from matplotlib)
  Downloading fonttools-4.63.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (118 kB)
Collecting kiwisolver>=1.3.1 (from matplotlib)
  Downloading kiwisolver-1.5.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (5.1 kB)
Collecting packaging>=20.0 (from matplotlib)
  Using cached packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
Collecting pillow>=9 (from matplotlib)
  Downloading pillow-12.3.0-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (9.1 kB)
Collecting pyparsing>=3 (from matplotlib)
  Using cached pyparsing-3.3.2-py3-none-any.whl.metadata (5.8 kB)
Collecting python-dateutil>=2.7 (from matplotlib)
  Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting six>=1.5 (from python-dateutil>=2.7->matplotlib)
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Downloading numpy-2.5.2-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (16.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.7/16.7 MB 1.7 MB/s eta 0:00:00
Downloading scipy-1.18.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (35.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.3/35.3 MB 2.2 MB/s eta 0:00:00
Downloading matplotlib-3.11.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (11.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.1/11.1 MB 2.2 MB/s eta 0:00:00
Downloading contourpy-1.3.3-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (363 kB)
Using cached cycler-0.12.1-py3-none-any.whl (8.3 kB)
Downloading fonttools-4.63.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (4.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 2.1 MB/s eta 0:00:00
Downloading kiwisolver-1.5.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.5/1.5 MB 1.8 MB/s eta 0:00:00
Using cached packaging-26.3-py3-none-any.whl (129 kB)
Downloading pillow-12.3.0-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (6.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.9/6.9 MB 1.9 MB/s eta 0:00:00
Using cached pyparsing-3.3.2-py3-none-any.whl (122 kB)
Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Installing collected packages: six, pyparsing, pillow, packaging, numpy, kiwisolver, fonttools, cycler, scipy, python-dateutil, contourpy, matplotlib
Successfully installed contourpy-1.3.3 cycler-0.12.1 fonttools-4.63.0 kiwisolver-1.5.0 matplotlib-3.11.1 numpy-2.5.2 packaging-26.3 pillow-12.3.0 pyparsing-3.3.2 python-dateutil-2.9.0.post0 scipy-1.18.1 six-1.17.0
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ cd sim
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ python3 plot_rc.py
figure ecrite dans docs/10-electronics/


python3 machine.py
Traceback (most recent call last):
  File "/home/lady_horacia/dev/sentinelle/sim/machine.py", line 19, in <module>
    from config import FS_ADC, F_ROT_NOM, NOISE_DENS_G
  File "/home/lady_horacia/dev/sentinelle/sim/config.py", line 1
    sim/config.py
IndentationError: unexpected indent
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ python3 machine.py
Traceback (most recent call last):
  File "/home/lady_horacia/dev/sentinelle/sim/machine.py", line 20, in <module>
    from bearing import Bearing, BEARING_6205, bearing_freqs
ImportError: cannot import name 'Bearing' from 'bearing' (/home/lady_horacia/dev/sentinelle/sim/bearing.py)
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ python3 machine.py
Traceback (most recent call last):
  File "/home/lady_horacia/dev/sentinelle/sim/machine.py", line 20, in <module>
    from bearing import bearing, BEARING_6205, bearing_freqs
ImportError: cannot import name 'bearing' from 'bearing' (/home/lady_horacia/dev/sentinelle/sim/bearing.py)
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ python3 machine.py
Delta f            = 6.25 Hz
f_rot demandee     = 25.0 Hz
raie dominante     = 25.000 Hz  (amplitude 0.1200 g)
ecart              = 0.000 Hz = 0.00 Delta f
critere (<= 1 Df)  : OK
amplitude attendue = 0.1200 g
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ 


ngspice -b butter3.cir

Note: No compatibility mode selected!


Circuit: * sentinelle - filtre anti-repliement butterworth 3e ordre, fc = 3,4 khz

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1321
out/butter3_ac.txt: No such file or directory
ngspice-45.2 done
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim/spice$ mkdir -p out
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim/spice$ ngspice -b butter3.cir

Note: No compatibility mode selected!


Circuit: * sentinelle - filtre anti-repliement butterworth 3e ordre, fc = 3,4 khz

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1321
ngspice-45.2 done
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim/spice$ python3 - <<'EOF'
import numpy as np, filter_model as fm
d = np.loadtxt("spice/out/butter3_ac.txt"); f, gs = d[:,0], d[:,1]
f0, Q = fm.sk_params(fm.NOM['R1'], fm.NOM['R2'], fm.NOM['C1'], fm.NOM['C2'])
print(f"cellule SK : f0 = {f0:.2f} Hz, Q = {Q:.4f}  (cible Q = 1,000)")
print(f"cellule RC : fc = {1/(2*np.pi*fm.NOM['R3']*fm.NOM['C3']):.2f} Hz")
print(f"cascade    : fc(-3dB) = {fm.fc_3db(**fm.NOM):.2f} Hz")
print("\nvalidation modele Python vs ngspice :")
print(f"{'f (Hz)':>8s} {'ngspice':>10s} {'modele':>10s} {'ecart':>8s}")
for ff in (100,1000,2500,3200,4000,12800,25600):
    a = np.interp(ff, f, gs); b = fm.att_db(ff, **fm.NOM)
    print(f"{ff:8d} {a:10.3f} {b:10.3f} {abs(a-b):8.4f}")
EOF
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'filter_model'
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim/spice$ cd ..
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ python3 - <<'EOF'
import numpy as np, filter_model as fm
d = np.loadtxt("spice/out/butter3_ac.txt"); f, gs = d[:,0], d[:,1]
f0, Q = fm.sk_params(fm.NOM['R1'], fm.NOM['R2'], fm.NOM['C1'], fm.NOM['C2'])
print(f"cellule SK : f0 = {f0:.2f} Hz, Q = {Q:.4f}  (cible Q = 1,000)")
print(f"cellule RC : fc = {1/(2*np.pi*fm.NOM['R3']*fm.NOM['C3']):.2f} Hz")
print(f"cascade    : fc(-3dB) = {fm.fc_3db(**fm.NOM):.2f} Hz")
print("\nvalidation modele Python vs ngspice :")
print(f"{'f (Hz)':>8s} {'ngspice':>10s} {'modele':>10s} {'ecart':>8s}")
for ff in (100,1000,2500,3200,4000,12800,25600):
    a = np.interp(ff, f, gs); b = fm.att_db(ff, **fm.NOM)
    print(f"{ff:8d} {a:10.3f} {b:10.3f} {abs(a-b):8.4f}")
EOF
cellule SK : f0 = 3392.85 Hz, Q = 0.9785  (cible Q = 1,000)
cellule RC : fc = 3386.28 Hz
cascade    : fc(-3dB) = 3340.74 Hz

validation modele Python vs ngspice :
  f (Hz)    ngspice     modele    ecart
     100     -0.000     -0.000   0.0000
    1000     -0.022     -0.022   0.0000
    2500     -0.788     -0.788   0.0000
    3200     -2.509     -2.509   0.0001
    4000     -5.845     -5.845   0.0001
   12800    -34.630    -34.630   0.0001
   25600    -52.681    -52.681   0.0000
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ python3 montecarlo.py
=== Monte-Carlo, 200 tirages, R +/-5 %, C +/-10 %, loi uniforme ===

  fc (-3 dB)               moyenne  3307.853 Hz  ecart-type  152.983 Hz  min  3000.186  max  3730.916
  f0 cellule Sallen-Key    moyenne  3374.730 Hz  ecart-type  156.139 Hz  min  3052.744  max  3758.570
  Q cellule Sallen-Key     moyenne     0.972  ecart-type    0.040  min     0.889  max     1.080
  attenuation a 25,6 kHz   moyenne   -52.772 dB  ecart-type    0.991 dB  min   -55.296  max   -50.118

  fc nominal                : 3340.74 Hz
  ecart relatif [min ; max] : [-10.19 % ; +11.68 %]
  centile 0,5 % / 99,5 %    : 3011.4 Hz / 3698.8 Hz
  dans +/-8 %             : 183/200 = 91.5 %  KO
  pire attenuation 25,6 kHz : -50.12 dB (objectif <= -48 dB : OK)
  Q max                     : 1.080 (bosse de 1.71 dB)
Traceback (most recent call last):
  File "/home/lady_horacia/dev/sentinelle/sim/montecarlo.py", line 71, in <module>
    np.savez("../out/montecarlo.npz", fc=res["fc"], Q=res["Q"],
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
             f0=res["f0_sk"], att=res["att_25k6"], fc_nom=fc_nom)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lady_horacia/dev/sentinelle/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 673, in savez
    _savez(file, args, kwds, False, allow_pickle=allow_pickle)
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lady_horacia/dev/sentinelle/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 779, in _savez
    zipf = zipfile_factory(file, mode="w", compression=compression)
  File "/home/lady_horacia/dev/sentinelle/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 112, in zipfile_factory
    return zipfile.ZipFile(file, *args, **kwargs)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/zipfile/__init__.py", line 1453, in __init__
    self.fp = io.open(file, filemode)
              ~~~~~~~^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '../out/montecarlo.npz'
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ cd /home/lady_horacia/dev/sentinelle/
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ mkdir -p out
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle$ cd sim
python3 montecarlo.py
=== Monte-Carlo, 200 tirages, R +/-5 %, C +/-10 %, loi uniforme ===

  fc (-3 dB)               moyenne  3307.853 Hz  ecart-type  152.983 Hz  min  3000.186  max  3730.916
  f0 cellule Sallen-Key    moyenne  3374.730 Hz  ecart-type  156.139 Hz  min  3052.744  max  3758.570
  Q cellule Sallen-Key     moyenne     0.972  ecart-type    0.040  min     0.889  max     1.080
  attenuation a 25,6 kHz   moyenne   -52.772 dB  ecart-type    0.991 dB  min   -55.296  max   -50.118

  fc nominal                : 3340.74 Hz
  ecart relatif [min ; max] : [-10.19 % ; +11.68 %]
  centile 0,5 % / 99,5 %    : 3011.4 Hz / 3698.8 Hz
  dans +/-8 %             : 183/200 = 91.5 %  KO
  pire attenuation 25,6 kHz : -50.12 dB (objectif <= -48 dB : OK)
  Q max                     : 1.080 (bosse de 1.71 dB)
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ ngspice -b butter3.cir
butter3.cir: No such file or directory
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim$ cd spice
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/sim/spice$ ngspice -b butter3.cir

Note: No compatibility mode selected!


Circuit: * sentinelle - filtre anti-repliement butterworth 3e ordre, fc = 3,4 khz

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1321
ngspice-45.2 done



arm-none-eabi-objdump -s -j .isr_vector build/node-fw.elf | head -6

build/node-fw.elf:     file format elf32-littlearm

Contents of section .isr_vector:
 8000000 00000220 cd000008 c9000008 c9000008  ... ............
 8000010 c9000008 c9000008 c9000008 00000000  ................


arm-none-eabi-objdump -h build/node-fw.elf | grep isr_vector
  0 .isr_vector   00000040  08000000  08000000  00010000  2**2


cd ~/dev/sentinelle/node-fw

# 1. Générer le linker temporaire avec une pile trop grande
sed 's/_stack_size = 4K;/_stack_size = 200K;/' linker/stm32f407_sections.ld > /tmp/bad_sections.ld

# 2. Créer le fichier .ld temporaire avec les chemins absolus
LINKER_DIR="/home/lady_horacia/dev/sentinelle/node-fw/linker"
cat << EOF > /tmp/bad.ld
INCLUDE ${LINKER_DIR}/stm32f407_mem.ld
REGION_ALIAS("APP", APP_A)
INCLUDE /tmp/bad_sections.ld
EOF

# 3. Récupérer tous les objets .o
OBJECTS=$(find build -name "*.o")

# 4. Linker
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
    -T /tmp/bad.ld -L"$LINKER_DIR" --specs=nano.specs \
    $OBJECTS -o /tmp/bad.elf 2>&1
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /tmp/bad.elf section `._stack' will not fit in region `RAM'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: ERREUR: RAM insuffisante pour .bss + tas + pile
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: ERREUR: table des vecteurs incomplete
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: region `RAM' overflowed by 78448 bytes
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: warning: cannot find entry symbol Reset_Handler; defaulting to 08020000
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-exit.o): in function `exit':
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/stdlib/exit.c:65:(.text+0x18): undefined reference to `_exit'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: (_exit): Unknown destination type (ARM/Thumb) in /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-exit.o)
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/stdlib/exit.c:65:(.text+0x18): dangerous relocation: unsupported relocation
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-readr.o): in function `_read_r':
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/readr.c:49:(.text+0x14): undefined reference to `_read'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: (_read): Unknown destination type (ARM/Thumb) in /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-readr.o)
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/readr.c:49:(.text+0x14): dangerous relocation: unsupported relocation
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-closer.o): in function `_close_r':
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/closer.c:47:(.text+0xc): undefined reference to `_close'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: (_close): Unknown destination type (ARM/Thumb) in /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-closer.o)
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/closer.c:47:(.text+0xc): dangerous relocation: unsupported relocation
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-lseekr.o): in function `_lseek_r':
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/lseekr.c:49:(.text+0x14): undefined reference to `_lseek'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: (_lseek): Unknown destination type (ARM/Thumb) in /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-lseekr.o)
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/lseekr.c:49:(.text+0x14): dangerous relocation: unsupported relocation
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-writer.o): in function `_write_r':
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/writer.c:49:(.text+0x14): undefined reference to `_write'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: (_write): Unknown destination type (ARM/Thumb) in /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-writer.o)
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/writer.c:49:(.text+0x14): dangerous relocation: unsupported relocation
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-sbrkr.o): in function `_sbrk_r':
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/sbrkr.c:51:(.text+0xc): undefined reference to `_sbrk'
/usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/bin/ld: (_sbrk): Unknown destination type (ARM/Thumb) in /usr/lib/gcc/arm-none-eabi/14.2.1/../../../arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc_nano.a(libc_a-sbrkr.o)
/build/newlib-Ipb6mw/newlib-4.6.0.20260123/build_nano/arm-none-eabi/thumb/v7e-m+fp/hard/newlib/../../../../../../newlib/libc/reent/sbrkr.c:51:(.text+0xc): dangerous relocation: unsupported relocation
collect2: error: ld returned 1 exit status


make vectors
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -std=c11 -Og -g3 -ffreestanding -fno-common -ffunction-sections -fdata-sections -fstack-usage -Wall -Wextra -Werror -Iinc -Idrivers -Ihal -Isys -Iapp -c startup/startup_stm32f4.c -o build/a/startup/startup_stm32f4.o
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -std=c11 -Og -g3 -ffreestanding -fno-common -ffunction-sections -fdata-sections -fstack-usage -Wall -Wextra -Werror -Iinc -Idrivers -Ihal -Isys -Iapp -c drivers/rcc.c -o build/a/drivers/rcc.o
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -std=c11 -Og -g3 -ffreestanding -fno-common -ffunction-sections -fdata-sections -fstack-usage -Wall -Wextra -Werror -Iinc -Idrivers -Ihal -Isys -Iapp -c drivers/gpio.c -o build/a/drivers/gpio.o
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -std=c11 -Og -g3 -ffreestanding -fno-common -ffunction-sections -fdata-sections -fstack-usage -Wall -Wextra -Werror -Iinc -Idrivers -Ihal -Isys -Iapp -c drivers/uart.c -o build/a/drivers/uart.o
drivers/uart.c:11:9: error: "USART2_SR" redefined [-Werror]
   11 | #define USART2_SR   (*(volatile uint32_t *)(USART2_BASE + 0x00u))
      |         ^~~~~~~~~
In file included from drivers/uart.c:3:
inc/stm32f407_regs.h:132:9: note: this is the location of the previous definition
  132 | #define USART2_SR       (*(volatile uint32_t *)(USART2_BASE + 0x00UL))
      |         ^~~~~~~~~
drivers/uart.c:12:9: error: "USART2_DR" redefined [-Werror]
   12 | #define USART2_DR   (*(volatile uint32_t *)(USART2_BASE + 0x04u))
      |         ^~~~~~~~~
inc/stm32f407_regs.h:133:9: note: this is the location of the previous definition
  133 | #define USART2_DR       (*(volatile uint32_t *)(USART2_BASE + 0x04UL))
      |         ^~~~~~~~~
drivers/uart.c:13:9: error: "USART2_BRR" redefined [-Werror]
   13 | #define USART2_BRR  (*(volatile uint32_t *)(USART2_BASE + 0x08u))
      |         ^~~~~~~~~~
inc/stm32f407_regs.h:134:9: note: this is the location of the previous definition
  134 | #define USART2_BRR      (*(volatile uint32_t *)(USART2_BASE + 0x08UL))
      |         ^~~~~~~~~~
drivers/uart.c:14:9: error: "USART2_CR1" redefined [-Werror]
   14 | #define USART2_CR1  (*(volatile uint32_t *)(USART2_BASE + 0x0Cu))
      |         ^~~~~~~~~~
inc/stm32f407_regs.h:135:9: note: this is the location of the previous definition
  135 | #define USART2_CR1      (*(volatile uint32_t *)(USART2_BASE + 0x0CUL))
      |         ^~~~~~~~~~
drivers/uart.c:15:9: error: "USART2_CR2" redefined [-Werror]
   15 | #define USART2_CR2  (*(volatile uint32_t *)(USART2_BASE + 0x10u))
      |         ^~~~~~~~~~
inc/stm32f407_regs.h:136:9: note: this is the location of the previous definition
  136 | #define USART2_CR2      (*(volatile uint32_t *)(USART2_BASE + 0x10UL))
      |         ^~~~~~~~~~
drivers/uart.c:16:9: error: "USART2_CR3" redefined [-Werror]
   16 | #define USART2_CR3  (*(volatile uint32_t *)(USART2_BASE + 0x14u))
      |         ^~~~~~~~~~
inc/stm32f407_regs.h:137:9: note: this is the location of the previous definition
  137 | #define USART2_CR3      (*(volatile uint32_t *)(USART2_BASE + 0x14UL))
      |         ^~~~~~~~~~
drivers/uart.c:19:9: error: "SR_RXNE" redefined [-Werror]
   19 | #define SR_RXNE     (1u << 5)
      |         ^~~~~~~
inc/stm32f407_regs.h:142:9: note: this is the location of the previous definition
  142 | #define SR_RXNE         (1UL << 5)
      |         ^~~~~~~
drivers/uart.c:20:9: error: "SR_TXE" redefined [-Werror]
   20 | #define SR_TXE      (1u << 7)
      |         ^~~~~~
inc/stm32f407_regs.h:141:9: note: this is the location of the previous definition
  141 | #define SR_TXE          (1UL << 7)
      |         ^~~~~~
drivers/uart.c: In function 'uart_init':
drivers/uart.c:55:18: error: 'UART_BRR_VALUE' undeclared (first use in this function)
   55 |     USART2_BRR = UART_BRR_VALUE;
      |                  ^~~~~~~~~~~~~~
drivers/uart.c:55:18: note: each undeclared identifier is reported only once for each function it appears in
cc1: all warnings being treated as errors
make: *** [Makefile:45: build/a/drivers/uart.o] Error 1
(.venv) lady_horacia@DESKTOP2Hora:~/dev/sentinelle/node-fw$ 


./app/main.c
./drivers/gpio.c
./drivers/iwdg.c
./drivers/rcc.c
./drivers/uart.c
./hal/hal_time.c
./linker/backup/slot_a.ld
./linker/backup/slot_b.ld
./linker/backup/stm32f407.ld
./linker/backup/stm32f407_mem.ld
./linker/backup/stm32f407_sections.ld
./linker/slot_a.ld
./linker/slot_b.ld
./linker/stm32f407.ld
./linker/stm32f407_mem.ld
./linker/stm32f407_sections.ld
./src/main.c
./src/startup.c
./startup/startup_stm32f4.c
./sys/fault.c
./sys/syscalls.c
./app/main.c
./drivers/gpio.c
./drivers/iwdg.c
./drivers/rcc.c
./drivers/uart.c
./hal/hal_time.c
./linker/backup/slot_a.ld
./linker/backup/slot_b.ld
./linker/backup/stm32f407.ld
./linker/backup/stm32f407_mem.ld
./linker/backup/stm32f407_sections.ld
./linker/slot_a.ld
./linker/slot_b.ld
./linker/stm32f407.ld
./linker/stm32f407_mem.ld
./linker/stm32f407_sections.ld
./src/main.c
./src/startup.c
./startup/startup_stm32f4.c
./sys/fault.c
./sys/syscalls.c

nb : j'ai tout ça mais ils sont vide
