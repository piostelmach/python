#!/usr/bin/python3.5

#####################################################################################
#Opis: Czujka w standardzie Nagios, sprawdzanie dzialania celli
#Dzialanie: ...
#Parametry: ./cells_ver2.py -fnCellStatus | -fnStatusDrives | -fnStatusHardDriveErrors | -fnPredictHDDFailure | -fnDriveSpace | -fnCheckBattery | -fnCheckBatteryError | -fnCheckBatteryCachePolicy | -fnCheckBatteryTemp | -fnCheckTemperature | -fnStatusASMDisk | -fnStatusStorageNodes | -fnStatusFlashDisks | -fnStatusFlashCache | -fnStatusInfiniband | -fnCheckInfinibandPort | -fnCheckMemoryErrors | -fnASMSpaceCheck | -fnCheckPSU | -fnCheckILOMErrors | -fnCheckPublicBond | -fnCheckIBBond | -fnCountFlashCache
#Autor: Piotr Stelmach (piotr.stelmach@accenture.com)
#wersja: 1.0
#Data ostatniej modyfikacji: 19.05.2017 
#Wymagania do uruchomienia czujki: ...
####################################################################################

from tabulate import tabulate #bilbioteka odpowiedzialna za rysowanie tabeli
import sys, getopt, os, re, uuid

opt=str(sys.argv[1])


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
   
def fnDriveSpace(): 
   print ("Not implemented yet")
   

def fnCheckBattery():
   print ("Not implemented yet")

def fnCheckBatteryError():
   print ("Not implemented yet")

def fnCheckBatteryCachePolicy():
   k = gen_tmp_file()
   command = os.popen(str(DCLI_ALL)+" /opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -Lall -aALL |grep 'Cache Policy' |grep -i current |grep -v WriteBack > "+str(k))
   command.read()
   set_nagios_status(k)
   
def fnCheckBatteryTemp():
   print ("Not implemented yet")

def fnCheckTemperature():
   print ("Not implemented yet")

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
   
def fnASMSpaceCheck(): #tutaj wystepuje uzycie dodatkowego skryptu check_asm.sh
   command = os.popen("su - oracle -c \"~oracle/edba/monitoring_scripts/other_scripts/check_asm.sh $ASM_SID $ASM_ORACLE_HOME\"")
   command.read()
   
def fnCheckPSU():
   print ("Not implemented yet")

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
   print (int(sys.argv[2]))
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

'''def rm_tmp(): #funkcja usuwajaca plik tmp_cells
   rm = os.popen("rm -f tmp_cells.txt")
   rm.read()  #wykonaj'''
   
'''def check_process():
    #command = os.popen("dcli -g allcells -l celladmin \"cellcli -e list cell attributes status,cellsrvStatus,msStatus,rsStatus \" > tmp_cells.txt")
    #command.read() #wykonanie powyzszego zapytania
  
   with open("tmp_cells.txt") as f: #uchwyt do pliku
    contents = f.read()
    running = sum(1 for x in re.finditer(r"\brunning\b", contents)) #zlicza wystapienie slowa running
    online = sum(1 for y in re.finditer(r"\bonline\b", contents)) #zlicza wystapienie slowa online
    if running == 9 and online == 3: #oryginalne zapytanie zwraca 9 statusow running oraz 3 online, jesli true to OK
       print ("OK")
       rm_tmp()
       sys.exit(0)
    else:
       print ("Critical") # w innym przypadku Critical
       rm_tmp()
       sys.exit(2)'''

'''def hlp():
    print ('\nPrzyklad.\n\n')
    print ('Poprawne działanie komendy dcli -g allcells -l celladmin \"cellcli -e list cell attributes status,cellsrvStatus,msStatus,rsStatus\" powinno zwrocic ponizszy output:\n ')
    print (tabulate([['exatmcell01', 'online', 'running', 'running', 'running'], ['exatmcell02', 'online', 'running', 'running', 'running'], ['exatmcell03', 'online', 'running', 'running', 'running']], headers=['Cells', 'Status', 'cellsrvStatus', 'msStatus', 'rsStatus'])+"\n")'''

if opt == '-h':
      print ('Correct use:' +str(sys.argv[0])+ ' -fnCellStatus | -fnStatusDrives | -fnStatusHardDriveErrors | -fnPredictHDDFailure | -fnDriveSpace | -fnCheckBattery | -fnCheckBatteryError | -fnCheckBatteryCachePolicy | -fnCheckBatteryTemp | -fnCheckTemperature | -fnStatusASMDisk | -fnStatusStorageNodes | -fnStatusFlashDisks | -fnStatusFlashCache | -fnStatusInfiniband | -fnCheckInfinibandPort | -fnCheckMemoryErrors | -fnASMSpaceCheck | -fnCheckPSU | -fnCheckILOMErrors | -fnCheckPublicBond | -fnCheckIBBond | -fnCountFlashCache')
      sys.exit()
elif opt == "-fnCellStatus":
         fnCellStatus()
elif opt == "-fnStatusDrives":
         fnStatusDrives()
elif opt == "-fnStatusHardDriveErrors":
         fnStatusHardDriveErrors()
elif opt == "-fnPredictHDDFailure":
         fnPredictHDDFailure()
elif opt == "-fnDriveSpace":
         fnDriveSpace()
elif opt == "-fnCheckBattery":
         fnCheckBattery()
elif opt == "-fnCheckBatteryError":
         fnCheckBatteryError()
elif opt == "-fnCheckBatteryCachePolicy":
         fnCheckBatteryCachePolicy()
elif opt == "-fnCheckBatteryTemp":
         fnCheckBatteryTemp()
elif opt == "-fnCheckTemperature":
         fnCheckTemperature()
elif opt == "-fnStatusASMDisk":
         fnStatusASMDisk()
elif opt == "-fnStatusStorageNodes":
         fnStatusStorageNodes()
elif opt == "-fnStatusFlashDisks":
         fnStatusFlashDisks()
elif opt == "-fnStatusFlashCache":
         fnStatusFlashCache()
elif opt == "-fnStatusInfiniband":
         fnStatusInfiniband()
elif opt == "-fnCheckInfinibandPort":
         fnCheckInfinibandPort()
elif opt == "-fnCheckMemoryErrors":
         fnCheckMemoryErrors()
elif opt == "-fnASMSpaceCheck":
         fnASMSpaceCheck()
elif opt == "-fnCheckPSU":
         fnCheckPSU()
elif opt == "-fnCheckILOMErrors":
         fnCheckILOMErrors()
elif opt == "-fnCheckPublicBond":
         fnCheckPublicBond()
elif opt == "-fnCheckIBBond":
         fnCheckIBBond()
elif opt == "-fnCountFlashCache":
         fnCountFlashCache()
         
else:
   print ('Correct use:' +str(sys.argv[0])+ ' -fnCellStatus | -fnStatusDrives | -fnStatusHardDriveErrors | -fnPredictHDDFailure | -fnDriveSpace | -fnCheckBattery | -fnCheckBatteryError | -fnCheckBatteryCachePolicy | -fnCheckBatteryTemp | -fnCheckTemperature | -fnStatusASMDisk | -fnStatusStorageNodes | -fnStatusFlashDisks | -fnStatusFlashCache | -fnStatusInfiniband | -fnCheckInfinibandPort | -fnCheckMemoryErrors | -fnASMSpaceCheck | -fnCheckPSU | -fnCheckILOMErrors | -fnCheckPublicBond | -fnCheckIBBond | -fnCountFlashCache')

