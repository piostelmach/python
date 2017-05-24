#!/usr/bin/python3.5

#####################################################################################
#Opis: Czujka w standardzie Nagios, sprawdzanie dzialania celli
#Parametry: ./cells_ver2.py fnCellStatus | fnStatusDrives  | fnStatusHardDriveErrors | fnPredictHDDFailure | fnDriveSpace <warning> | fnCheckBattery #<warning> | fnCheckBatteryError <warning> | fnCheckBatteryCachePolicy | fnCheckBatteryTemp <warning> | fnCheckTemperature <warning> | #fnStatusASMDisk | fnStatusStorageNodes | fnStatusFlashDisks | fnStatusFlashCache | fnStatusInfiniband | fnCheckInfinibandPort | fnCheckMemoryErrors #| fnCheckPSU | fnCheckILOMErrors | fnCheckPublicBond | fnCheckIBBond | fnCountFlashCache
#Autor: Piotr Stelmach ppiotr.stelmach@gmail.com
#wersja: 1.0
#Data ostatniej modyfikacji: 23.05.2017 
#Wymagania do uruchomienia czujki: ...
####################################################################################

import sys, getopt, os, re, uuid

opt = str(sys.argv[1]) #parametr wejsciowy(nazwa funkcji) dla skryptu

DCLI_ALL="/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/all_group -l root"
DCLI_CELL="/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/cell_group -l root"
DCLI_DB="/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/dbs_group -l root"
GRID_HOME="/u01/app/12.2.0.1/grid"


def set_nagios_status(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie
   if os.stat(str(filename)).st_size == 0: #jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   else:
      os.remove(str(filename))
      print ("Critical")
      sys.exit(2)

def set_nagios_status2(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie
   if 'WARNING' in open(str(filename)).read(): #jesli wystepuje slowo WARNING ustaw WARNING
          print ("WARNING")
          os.remove(str(filename))
          sys.exit(1)
   else:
          print ("OK") #w innym przypadku OK
          sys.exit(0)

def gen_tmp_file(): #generuje i zwraca uuid wykorzystywany do nazw plikow tmp
   rand_uuid=uuid.uuid4() #utorzenie samej nazwy
   os.mknod(str(rand_uuid)) #plik uuid zostaje utworzony
   return rand_uuid #return nazwy pliku uuid

def fnCellStatus():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_CELL)+" cellcli -e list cell detail|grep -i stat|sort +1 -2|egrep -v '(running|off|normal|online|success)' > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnStatusDrives():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" /opt/MegaRAID/MegaCli/MegaCli64 PDList -aAll|grep \"Firmware state\"|egrep -v '(Online, Spun Up|Hotspare, Spun Up|Hotspare, Spun down)' > "+str(k))
   command.read()
   set_nagios_status(k)

def fnStatusHardDriveErrors():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" /opt/MegaRAID/MegaCli/MegaCli64 PDList -aAll|egrep '(Error|Failure)' | egrep -v '(Count: 0|Number: 0)' > "+str(k))
   command.read()
   set_nagios_status(k)

def fnPredictHDDFailure():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_CELL)+" cellcli -e list physicaldisk | grep -v normal > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnDriveSpace(warning): 
   k = gen_tmp_file()
   command = os.popen("for i in `/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/all_group -l root df -Phl | grep -Po '\s\d+%\s' | grep -Po '\d+'`; do if [ $i -gt "+str(warning)+" ] ; then echo \"WARNING\" >> "+str(k)+" ; else echo \"OK\"; fi done ") #zapis do pliku tylko statusu warning
   command.read()
   set_nagios_status2(k)

def fnCheckBattery(warning):
   k = gen_tmp_file()
   command = os.popen("for i in `/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/all_group -l root /opt/MegaRAID/MegaCli/MegaCli64 -AdpBbuCmd -a0|grep \"Full Charge Capacity\" | grep -Po '\d+\smAh' | grep -Po '\d+'`; do if [ $i -lt "+str(warning)+" ] ; then echo \"WARNING\" > "+str(k)+" ; else echo \"OK\"; fi done ") # pobierz wartosc dla mAh i zapisz do 
   command.read()
   set_nagios_status2(k)
   

def fnCheckBatteryError(warning):
   k = gen_tmp_file()
   command = os.popen("for i in `/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/all_group -l root /opt/MegaRAID/MegaCli/MegaCli64 -AdpBbuCmd -a0|grep \"Max Error\" | grep -Po 'Max\sError:\s\d+\s\%' | grep -Po '\d+' `; do if [ $i -gt "+str(warning)+" ] ; then echo \"WARNING\" > "+str(k)+" ; else echo \"OK\"; fi done") # pobierz wartosc % bledow, jesli wieksza niz warning to zapisz Warning do pliku
   command.read()
   set_nagios_status2(k)

def fnCheckBatteryCachePolicy():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" /opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -Lall -aALL |grep 'Cache Policy' |grep -i current |grep -v WriteBack > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnCheckBatteryTemp(warning):
   k = gen_tmp_file()
   command = os.popen("for i in `/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/all_group -l root  /opt/MegaRAID/MegaCli/MegaCli64 -AdpBbuCmd -a0 | grep Temperature: | grep -Po '\d+\sC' | grep -Po '\d+'`; do if [ $i -gt "+str(warning)+" ] ; then echo \"WARNING\" > "+str(k)+" ; else echo \"OK\"; fi done") # pobierz wartosc temperatury baterii, jesli jest wieksza niz warning zapisza Warning do pliku
   command.read()
   set_nagios_status2(k)

def fnCheckTemperature(warning):
   k = gen_tmp_file()
   command = os.popen("for i in `/usr/local/bin/dcli -g /opt/oracle.SupportTools/onecommand/all_group -l root 'ipmitool sunoem cli \"show /SYS/T_AMB\" |grep value' | grep -Po '\d+.\d+\sdegree\sC' | grep -Po '^\d+'`; do if [ $i -gt "+str(warning)+" ] ; then echo \"WARNING\" > "+str(k)+" ; else echo \"OK\"; fi done") # pobierz wartosc temperatury, jesli jest wkiesza niz warning to zapisz Warning do pliku
   command.read()
   set_nagios_status2(k)

def fnStatusASMDisk():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_CELL)+" cellcli -e list griddisk attributes name, ASMDeactivationOutcome, ASMModeStatus | grep -v ONLINE > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnStatusStorageNodes():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_CELL)+" cellcli -e \"list metriccurrent attributes all where objectType = \'CELL\' \" |grep -v normal > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnStatusFlashDisks():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_CELL)+" cellcli -e \"list celldisk where disktype=flashdisk\" | grep -v normal > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnStatusFlashCache():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_CELL)+" cellcli -e \"list flashcache detail\" |egrep \"status|size\" | grep -v \"normal\" | grep -v \"364.75G\" > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnStatusInfiniband():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" ibstatus | grep state | egrep -v '(LinkUp|ACIVE)' | grep -v \"4: ACTIVE\" > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnCheckInfinibandPort():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" ibcheckstate | grep \"#\" | egrep -v '(0 bad nodes found|0 ports with bad state found)' > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnCheckMemoryErrors():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" ipmitool sel list | grep ECC | cut -f1 -d : | sort -u > "+str(k))
   command.read()
   set_nagios_status(k)
   
   
def fnCheckPSU():
   k1 = gen_tmp_file()
   k2 = gen_tmp_file()
   command1 = os.popen(str(DCLI_ALL)+" 'ipmitool sunoem cli \"show /SYS/PS0\" |grep \"fault_state\" |grep -v \"OK\"' > "+str(k1))
   command2 = os.popen(str(DCLI_ALL)+" 'ipmitool sunoem cli \"show /SYS/PS1\" |grep \"fault_state\" |grep -v \"OK\"' > "+str(k2))
   command1.read()
   command2.read()
   
   if os.stat(str(k1)).st_size == 0 and os.stat(str(k2)).st_size == 0: #jesli wygenerowany plik k1 i k2 jest pusty to jest OK
      print ("OK")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(0) 
   elif os.stat(str(k1)).st_size > 0 and os.stat(str(k2)).st_size > 0: #jesli wygenerowany plik k1 i k2 cos zawiera to Critical
      print ("Critical")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(2) 
   else: #w innym przypadku Warning
      print ("Warning")
      sys.exit(1)
    

def fnCheckILOMErrors():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" 'ipmitool sunoem cli \"show faulty\" | grep -v \"| Property\" | grep -v \"\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\" | grep -v \"Connected\" | grep -v \"show faulty\" | grep -v \"Session closed\" | grep -v \"Disconnected\" | grep \"|\"' > "+str(k))
   command.read()
   set_nagios_status(k)

def fnCheckPublicBond():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_DB)+" cat /proc/net/bonding/${bondedPubIface} | grep \"MII Stat\" | grep -v up > "+str(k))
   command.read()
   set_nagios_status(k) 
   
def fnCheckIBBond():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_DB)+" cat /proc/net/bonding/${bondedIBIface} | grep \"MII Stat\" | grep -v up > "+str(k))
   command.read()
   set_nagios_status(k) 
   
def fnCountFlashCache():
   command1 = os.popen("cat /opt/oracle.SupportTools/onecommand/cell_group | grep -v -e '^$' | wc -l")
   command2 = os.popen(str(DCLI_CELL)+" \"cellcli -e list flashcache\" | wc -l")
   cell_count = int(command1.read())
   flash_cache_count = int(command2.read())
   
   if cell_count != flash_cache_count:
      print ("Warning")
      sys.exit(1)
   else:
      print ("OK")
      sys.exit(0)

if opt == 'h':
      print ('Correct use:' +str(sys.argv[0])+ ' fnCellStatus | fnStatusDrives | fnStatusHardDriveErrors | fnPredictHDDFailure | fnDriveSpace | fnCheckBattery | fnCheckBatteryError | fnCheckBatteryCachePolicy | fnCheckBatteryTemp | fnCheckTemperature | fnStatusASMDisk | fnStatusStorageNodes | fnStatusFlashDisks | fnStatusFlashCache | fnStatusInfiniband | fnCheckInfinibandPort | fnCheckMemoryErrors | fnCheckPSU | fnCheckILOMErrors | fnCheckPublicBond | fnCheckIBBond | fnCountFlashCache')
      sys.exit()
elif opt == "fnCellStatus":
         fnCellStatus()
elif opt == "fnStatusDrives":
         fnStatusDrives()
elif opt == "fnStatusHardDriveErrors":
         fnStatusHardDriveErrors()
elif opt == "fnPredictHDDFailure":
         fnPredictHDDFailure()
elif opt == "fnDriveSpace":
         fnDriveSpace(str(sys.argv[2]))
elif opt == "fnCheckBattery":
         fnCheckBattery(str(sys.argv[2]))
elif opt == "fnCheckBatteryError":
         fnCheckBatteryError(str(sys.argv[2]))
elif opt == "fnCheckBatteryCachePolicy":
         fnCheckBatteryCachePolicy()
elif opt == "fnCheckBatteryTemp":
         fnCheckBatteryTemp(str(sys.argv[2]))
elif opt == "fnCheckTemperature":
         fnCheckTemperature(str(sys.argv[2]))
elif opt == "fnStatusASMDisk":
         fnStatusASMDisk()		 
elif opt == "fnStatusStorageNodes":
         fnStatusStorageNodes()
elif opt == "fnStatusFlashDisks":
         fnStatusFlashDisks()
elif opt == "fnStatusFlashCache":
         fnStatusFlashCache()
elif opt == "fnStatusInfiniband":
         fnStatusInfiniband()
elif opt == "fnCheckInfinibandPort":
         fnCheckInfinibandPort()
elif opt == "fnCheckMemoryErrors":
         fnCheckMemoryErrors()
elif opt == "fnCheckPSU":
         fnCheckPSU()
elif opt == "fnCheckILOMErrors":
         fnCheckILOMErrors()
elif opt == "fnCheckPublicBond":
         fnCheckPublicBond()
elif opt == "fnCheckIBBond":
         fnCheckIBBond()
elif opt == "fnCountFlashCache":
         fnCountFlashCache()
         
else:
   print ('Correct use:' +str(sys.argv[0])+ ' fnCellStatus | fnStatusDrives | fnStatusHardDriveErrors | fnPredictHDDFailure | fnDriveSpace | fnCheckBattery | fnCheckBatteryError | fnCheckBatteryCachePolicy | fnCheckBatteryTemp | fnCheckTemperature | fnStatusASMDisk | fnStatusStorageNodes | fnStatusFlashDisks | fnStatusFlashCache | fnStatusInfiniband | fnCheckInfinibandPort | fnCheckMemoryErrors | fnCheckPSU | fnCheckILOMErrors | fnCheckPublicBond | fnCheckIBBond | fnCountFlashCache')
