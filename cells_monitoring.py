#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################################################################
#Opis: Czujka w standardzie Nagios, sprawdzanie dzialania celli
#Parametry: ./cells_ver2.py fnCellStatus <cellname> | fnStatusDrives | fnStatusHardDriveErrors | fnPredictHDDFailure <cellname> | fnDriveSpace <warning> <critical> <fs_name> | fnCheckTemperature <warning> | fnStatusASMDisk <cellname> | fnStatusStorageNodes <cellname> | fnStatusFlashDisks <cellname> | fnStatusFlashCache <cellname> | fnStatusInfiniband | fnCheckInfiniband | fnCheckMemoryErrors | fnCheckPSU | fnCheckILOMErrors | fnCheckPublicBond | fnCountFlashCache
#Autor: Piotr Stelmach ppiotr[dot]stelmach[at]gmail[dot]com
#wersja: 1.0.3
#Data ostatniej modyfikacji: 07.06.2017 
#
####################################################################################

import sys, getopt, os, re, uuid

username="root" #uzytkownik wykorzystywany do nawiazania połaczeń do serwerów exadaty

def set_nagios_status1(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie OK | CRITICAL
   if os.stat(str(filename)).st_size == 0: #jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   else:
      os.remove(str(filename))
      print ("Critical")
      sys.exit(2)

def set_nagios_status2(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie OK | WARNING | CRITICAL, wykorzystane przy celli
   if os.stat(str(filename)).st_size == 0: #jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   if os.stat(str(filename)).st_size >= 1: #jesli cos zapisalo sie do pliku to sprawdz czy wystepuje slowo offline dotyczace statusu celli
      if 'offline' in open(filename).read():
         os.remove(str(filename))
         print("Critical | status cells is offline")
         sys.exit(2)
      else:
         f = open(filename,'r') #otworz plik do odczytu
         file_contents = f.read()
         print("Warning | "+str(file_contents))
         f.close()
         os.remove(str(filename))
         sys.exit(1)

def set_nagios_status3(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie OK | WARNING
   if os.stat(str(filename)).st_size == 0: #jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   else: #jesli co zapisalo sie do pliku
      f = open(filename,'r') #otworz plik do odczytu
      file_contents = f.read()
      print("Warning | "+str(file_contents))
      f.close()
      os.remove(str(filename))
      sys.exit(1)

def set_nagios_status4(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie OK | WARNING
   if os.stat(str(filename)).st_size == 0: #jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   else: #jesli co zapisalo sie do pliku
      f = open(filename,'r') #otworz plik do odczytu
      file_contents = f.read()
      print("Critical | "+str(file_contents))
      f.close()
      os.remove(str(filename))
      sys.exit(2)
   
def gen_tmp_file(): #generuje i zwraca uuid wykorzystywany do nazw plikow tmp
   rand_uuid=uuid.uuid4() #utorzenie samej nazwy
   os.mknod(str(rand_uuid)) #plik uuid zostaje utworzony
   return rand_uuid #return nazwy pliku uuid


def fnCellStatus(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e list cell detail|grep -i stat|sort +1 -2|egrep -v '(running|off|normal|online|success)' |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status2(k)
   
def fnStatusDrives(srvname):
   row = 1 #zmienna bedzie okreslac poziom wiersza w pliku, inicjalizacja od 1 (pierwszy wiersz pliku k1)
   k1 = gen_tmp_file() # generowany output z glownej komendy MegaCli64 PDList
   k2 = gen_tmp_file() # jesli w pliku k1 znajdzie sie jakis offline to wrzuci nazwe dysku to pliku k2
   command1 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" /opt/MegaRAID/MegaCli/MegaCli64 PDList -aAll|egrep '(Firmware state|Inquiry)'|egrep -v '(Online, Spun Up|Hotspare, Spun Up|Hotspare, Spun down)' |cut -d ' ' -f2- > "+str(k1))
   command1.read()
   
   file = open(str(k1), "r") #uchwyt do pliku k1 ktory bedziemy walidowac
   
   for line in file:
      row+=1 #przejdz wiersz nizej
      if "Offline" in line:  #jesli w pliku k1 wystapi slowo "Offline"
         command2=os.popen("sed '"+str(row)+"q;d' "+str(k1)+" | awk {'print $5'} >> "+str(k2)) #zapisz do pliku k2 nazwe dysku ktory jest Offline
         command2.read() #wykonaj komende
      else:
         pass
   file.close()	 
   
   if os.stat(str(k2)).st_size > 0:#jesli plik k2 istnieje
      f = open(str(k2),'r') #otworz plik do odczytu
      file_contents = f.read()
      print("Warning | "+str(file_contents))
      f.close()
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(1)
   else: # jesli pliku k2 nie ma
      print ("OK")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(0)
   

def fnStatusHardDriveErrors(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" /opt/MegaRAID/MegaCli/MegaCli64 PDList -aAll|egrep '(Error|Failure)' | egrep -v '(Count: 0|Number: 0)' |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnPredictHDDFailure(cellname): ###dcli: error: no such option: -e##
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" -e list physicaldisk | grep -v normal | cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnDriveSpace(srvname, warning, critical, fs_mounted_on): #funkcja pobiera prog warning, prog ciritcal, nazwa filesystemu
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" df -h | grep -P '(^|\s)\K"+str(fs_mounted_on)+"(?=\s|$)'| tr -d '%' | awk '{print $5}' > "+str(k)) #szukaj dokladnie podanego wzorca
   command.read()
   
   f = open(str(k))
   count = f.read()
   
   if int(count) >= int(warning) and int(count) <= int(critical):
      print("Warning | filesystem: "+str(count).rstrip()+"%") #rstrip() usuwa biale znaki, nowa linie, tab..
      os.remove(str(k))
      sys.exit(1)
   elif int(count) >= int(critical) and int(count) > int(warning):
      print("Critical | filesystem: "+str(count).rstrip()+"%")
      os.remove(str(k))
      sys.exit(2)
   else:
      print("Ok | filesystem: "+str(count).rstrip()+"%")
      os.remove(str(k))
      sys.exit(0)
   
def fnCheckTemperature(srvname, warning):#funkcja pobiera prog warning ## Could not open device at /dev/ipmi0 or /dev/ipmi/0 or /dev/ipmidev/0: 
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" \"ipmitool sunoem cli show\ /SYS/T_AMB |grep value | grep -Po '\d+.\d+\sdegree\sC' | grep -Po '^\d+'\" |cut -d ' ' -f2- > "+str(k))
   command.read()
   
   f = open(str(k))
   count = f.read()
   
   if int(count) >= int(warning):
      print("Warning | temperature: "+str(count).rstrip()+"C")
      os.remove(str(k))
      sys.exit(1)
   else:
      print("Ok | temperature: "+str(count).rstrip()+"C")
      os.remove(str(k))
      sys.exit(0)

def fnStatusASMDisk(cellname): ##dcli: error: no such option: -e
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+"cellcli -e list griddisk attributes name, ASMDeactivationOutcome, ASMModeStatus | grep -v ONLINE |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnStatusStorageNodes(cellname): ## dcli: error: no such option: -e
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+"cellcli -e \"list metriccurrent attributes all where objectType = \'CELL\' \" |grep -v normal |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnStatusFlashDisks(cellname): ##dcli: error: no such option: -e
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+"cellcli -e \"list celldisk where disktype=flashdisk\" | grep -v normal |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnStatusFlashCache(cellname): ## 
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+"cellcli -e \"list flashcache detail\" |egrep \"status|size\" | grep -v \"normal\" | grep -v \"5.817901611328125T\" |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnStatusInfiniband(srvname): ##Error: No command specified.
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+"ibstatus | grep state | egrep -v '(LinkUp|ACIVE)' | grep -v \"4: ACTIVE\" |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnCheckInfiniband(srvname): 
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+"/opt/oracle.SupportTools/ibdiagtools/verify-topology |sed '1d' |egrep -v '(SUCCESS|NOT APPLICABLE)' |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
   
def fnCheckMemoryErrors(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+"ipmitool sel list | grep PCI | cut -f1 -d : | sort -u |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)
     
def fnCheckPSU(srvname):
   k1 = gen_tmp_file()
   k2 = gen_tmp_file()
   command1 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" 'ipmitool sunoem cli show\ /SYS/PS0 |grep fault_state |grep -v \"OK\"' > "+str(k1))
   command2 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" 'ipmitool sunoem cli show\ /SYS/PS1 |grep fault_state |grep -v \"OK\"' > "+str(k2))
   command1.read()
   command2.read()
   
   if os.stat(str(k1)).st_size == 0 and os.stat(str(k2)).st_size == 0: #jesli wygenerowany plik k1 i k2 jest pusty to jest OK
      print ("OK | PS1 and PS0 are UP")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(0) 
   elif os.stat(str(k1)).st_size > 0 and os.stat(str(k2)).st_size == 0: #jesli wygenerowany plik k1 cos zawiera
      print ("Warning | PS0 down")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(1) 
   elif os.stat(str(k1)).st_size == 0 and os.stat(str(k2)).st_size > 0: #jesli wygenerowany plik k2 cos zawiera
      print ("Warning | PS1 down")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(1)
   else: #w innym przypadku Critical
      print ("Critical | PS1 and PS2 are DOWN")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(2)

def fnCheckILOMErrors(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+"'ipmitool sunoem cli show\ faulty | egrep -v '(Connected|show faulty|closed|Disconnected)' > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnCheckPublicBond():
   k = gen_tmp_file()
   command = os.popen("cat /proc/net/bonding/bondeth0 | grep 'MII Stat' | grep -v up > "+str(k))
   command.read()
   set_nagios_status4(k) 
   
def fnCountFlashCache():
   command1 = os.popen("cat /opt/oracle.SupportTools/onecommand/cell_group | grep -v -e '^$' | wc -l")
   command2 = os.popen("dcli -l "+str(username)+" -g /opt/oracle.SupportTools/onecommand/cell_group list flashcache | wc -l")
   cell_count = int(command1.read())
   flash_cache_count = int(command2.read())
   
   if cell_count != flash_cache_count:
      print ("Warning | cell_count: "+str(cell_count)+ " | flashe_cache_count: "+str(flash_cache_count))
      sys.exit(1)
   else:
      print ("OK")
      sys.exit(0)

if str(sys.argv[1]) == "fnCellStatus":
         fnCellStatus(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnStatusDrives":
         fnStatusDrives(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnStatusHardDriveErrors":
         fnStatusHardDriveErrors(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnPredictHDDFailure":
         fnPredictHDDFailure(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnDriveSpace":
         fnDriveSpace(str(sys.argv[2]),str(sys.argv[3]),str(sys.argv[4]),str(sys.argv[5]))
elif str(sys.argv[1]) == "fnCheckTemperature":
         fnCheckTemperature(str(sys.argv[2]),str(sys.argv[3]))
elif str(sys.argv[1]) == "fnStatusASMDisk":
         fnStatusASMDisk(str(sys.argv[2]))		 
elif str(sys.argv[1]) == "fnStatusStorageNodes":
         fnStatusStorageNodes(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnStatusFlashDisks":
         fnStatusFlashDisks(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnStatusFlashCache":
         fnStatusFlashCache(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnStatusInfiniband":
         fnStatusInfiniband(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnCheckInfiniband":
         fnCheckInfiniband(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnCheckMemoryErrors":
         fnCheckMemoryErrors(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnCheckPSU":
         fnCheckPSU(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnCheckILOMErrors":
         fnCheckILOMErrors(str(sys.argv[2]))
elif str(sys.argv[1]) == "fnCheckPublicBond":
         fnCheckPublicBond()
elif str(sys.argv[1]) == "fnCountFlashCache":
         fnCountFlashCache()
else:
      print ('Correct use:' +str(sys.argv[0])+ ' fnCellStatus <cellname> | fnStatusDrives <srvname>| fnStatusHardDriveErrors <srvname> | fnPredictHDDFailure <cellname> | fnDriveSpace <srvname> <warning> <critical> <fs_name> | fnCheckTemperature <warning> | fnStatusASMDisk <cellname> | fnStatusStorageNodes <cellname> | fnStatusFlashDisks <cellname> | fnStatusFlashCache <cellname> | fnStatusInfiniband <srvname> | fnCheckInfiniband <srvname> | fnCheckMemoryErrors <srvname> | fnCheckPSU <srvname> | fnCheckILOMErrors <srvname> | fnCheckPublicBond | fnCountFlashCache')
