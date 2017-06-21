#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################################################################
#Opis: Czujka w standardzie Nagios, sprawdzanie dzialania celli
#Parametry: ./cells_ver2.py fnCellStatus <cellname> | fnStatusDrives | fnStatusHardDriveErrors | fnPredictHDDFailure <cellname> | fnDriveSpace <warning> <critical> <fs_name> | fnCheckTemperature <warning> | fnStatusASMDisk <cellname> | fnStatusStorageNodes <cellname> | fnStatusFlashDisks <cellname> | fnStatusFlashCache <cellname> | fnStatusInfiniband | fnCheckInfiniband | fnCheckMemoryErrors | fnCheckPSU | fnCheckILOMErrors | fnCheckPublicBond | fnCountFlashCache
#Autor: Piotr Stelmach ppiotr[dot]stelmach[at]gmail[dot]com
#wersja: 1.0.5
#Data ostatniej modyfikacji: 20.06.2017 
# - dodanie bloku try except dla funkcji set_nagios_status3, fnCheckTemperature
# - os.path.isfile sprawdzanie czy plik istnieje
# - fnDriveSpace dodanie parametru -P przy grep w przypadku fs'ow podmapowanych (nie pokazuje pustej kolumny)
####################################################################################

import sys, getopt, os, re, uuid
min_wartosc = 0
max_wartosc = 100

username="root" #uzytkownik wykorzystywany do nawiazania połaczeń do serwerów exadaty

def set_nagios_status1(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie Ok : Critical : UNKNOWN
   if os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size == 0: #jesli plik istnieje jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   elif os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size > 0: #jesli plik istnieje i cos zawiera
      os.remove(str(filename))
      print ("Critical")
      sys.exit(2)
   elif os.path.isfile(str(filename)) == False: #jesli nie wygenerowalo pliku
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def set_nagios_status2(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie Ok : Warning : Critical : UNKNOWN wykorzystane przy celli
   if os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size == 0: #jesli plik istnieje jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   elif os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size > 0: #jesli plik istnieje i jesli cos zapisalo sie do pliku to sprawdz czy wystepuje slowo offline dotyczace statusu celli
      if 'offline' in open(filename).read():
         os.remove(str(filename))
         print("Critical : status cells is offline")
         sys.exit(2)
      else:
         f = open(filename,'r') #otworz plik do odczytu
         file_contents = f.read()
         print("Warning : "+str(file_contents))
         f.close()
         os.remove(str(filename))
         sys.exit(1)
   elif os.path.isfile(str(filename)) == False: #jesli nie wygenerowalo pliku
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def set_nagios_status3(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie Ok : Warning : UNKNOWN
   if os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size == 0: #jesli plik istnieje jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   elif os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size > 0: #jesli plik istnieje i jesli cos zapisalo sie do pliku
      try:
         f = open(filename,'r') #otworz plik do odczytu
         file_contents = f.read()
         print("Warning : "+str(file_contents))
         f.close()
         os.remove(str(filename))
         sys.exit(1)
      except:
         print ("Unknown: Wystapil problem z wykonaniem polecenia")
         os.remove(str(filename))
         sys.exit(3)
   elif os.path.isfile(str(filename)) == False: #jesli nie wygenerowalo pliku
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def set_nagios_status4(filename): #funkcja pobiera nazwe pliku tmp, nastepnie ustawia status w nagiosie Ok : WARNING
   if os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size == 0: #jesli plik istnieje jesli plik jest pusty
      os.remove(str(filename))
      print ("OK")
      sys.exit(0)
   elif os.path.isfile(str(filename)) == True and os.stat(str(filename)).st_size > 0: #jesli plik istnieje i jesli cos zapisalo sie do pliku
      f = open(filename,'r') #otworz plik do odczytu
      file_contents = f.read()
      print("Critical : "+str(file_contents))
      f.close()
      os.remove(str(filename))
      sys.exit(2)
   elif os.path.isfile(str(filename)) == False: #jesli nie wygenerowalo pliku
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def gen_tmp_file(): #generuje i zwraca uuid wykorzystywany do nazw plikow tmp
   rand_uuid=uuid.uuid4() #utorzenie samej nazwy
   os.mknod(str(rand_uuid)) #plik uuid zostaje utworzony
   return rand_uuid #return nazwy pliku uuid


def fnCellStatus(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e list cell detail|grep -i stat|sort +1 -2|cut -d ' ' -f2- |egrep -v '(running|off|normal|online|success)'  > "+str(k))
   command.read()
   set_nagios_status2(k)

def fnStatusDrives(srvname):
   
   k1 = gen_tmp_file() # generowany output z glownej komendy MegaCli64 PDList
   k2 = gen_tmp_file() # jesli w pliku k1 znajdzie sie jakis offline to wrzuci nazwe dysku to pliku k2
   command1 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" /opt/MegaRAID/MegaCli/MegaCli64 PDList -aAll|egrep '(Firmware state|Inquiry)'|cut -d ' ' -f2- |egrep -v '(Online, Spun Up|Hotspare, Spun Up|Hotspare, Spun down)'  > "+str(k1))
   command1.read()
   command2=os.popen("grep -v Inquiry "+str(k1)+" >> "+str(k2)) #sprawdzenie czy w pliku jest coś poza nazwami dysków
   command2.read() #wykonaj komende

   if os.path.isfile(str(k2)) == True and os.stat(str(k2)).st_size > 0: #jesli plik istnieje i jesli cos zapisalo sie do pliku
      f = open(str(k1),'r') #otworz plik do odczytu
      file_contents = f.read()
      print("Warning : "+str(file_contents))
      f.close()
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(1)
   elif os.path.isfile(str(k2)) == True and os.stat(str(k2)).st_size == 0: # jesli pliku k2 istnieje i jest pusty
      print ("OK")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(0)
   elif os.path.isfile(str(filename)) == False: #jesli nie wygenerowalo pliku
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def fnStatusHardDriveErrors(srvname):
   k1 = gen_tmp_file()
   k2 = gen_tmp_file() # jesli w pliku k1 znajdzie sie jakis offline to wrzuci nazwe dysku to pliku k2
   command1 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" /opt/MegaRAID/MegaCli/MegaCli64 PDList -aAll|egrep '(Error|Failure)' | egrep -v '(Count: 0|Number: 0)' |cut -d ' ' -f2- > "+str(k1))
   command1.read()
   command2=os.popen("grep -v Inquiry "+str(k1)+" >> "+str(k2)) #sprawdzenie czy w pliku jest coś poza nazwami dysków
   command2.read() #wykonaj komende

   if os.path.isfile(str(k2)) == True and os.stat(str(k2)).st_size > 0: #jesli plik k2 istnieje i jesli cos zapisalo sie do pliku
      f = open(str(k2),'r') #otworz plik k2 do odczytu
      file_contents = f.read()
      print("Warning : "+str(file_contents))
      f.close()
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(1)
   elif os.path.isfile(str(k2)) == True and os.stat(str(k2)).st_size == 0: # jesli plik k2 istnieje i jest pusty
      print ("OK")
      os.remove(str(k1))
      os.remove(str(k2))
      sys.exit(0)
   elif os.path.isfile(str(k2)) == False: #jesli nie wygenerowalo pliku k2
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def fnPredictHDDFailure(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e list physicaldisk | grep -v normal | cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnDriveSpace(srvname, warning, critical, fs_mounted_on): #funkcja pobiera prog warning, prog ciritcal, nazwa filesystemu
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" df -h -P | grep -P '(^|\s)\K"+str(fs_mounted_on)+"(?=\s|$)'|cut -d ' ' -f2- |tr -d '%' | awk '{print $5}' > "+str(k)) #szukaj dokladnie podanego wzorca
   command.read()
   
   if os.path.isfile(str(k)) == True and os.stat(str(k)).st_size > 0: #jesli plik k istnieje i jesli cos zapisalo sie do pliku
      f = open(str(k))
      count = f.read()
      if int(count) >= int(warning) and int(count) <= int(critical):
         print("Warning - filesystem usage "+str(count).rstrip()+"%"+" |/="+str(count).rstrip()+"%"+";"+str(warning)+";"+str(critical)+";"+str(min_wartosc)+";"+str(max_wartosc)) #rstrip() usuwa biale znaki, nowa linie, tab..
         os.remove(str(k))
         sys.exit(1)
      elif int(count) >= int(critical) and int(count) > int(warning):
         print("Critical - filesystem usage "+str(count).rstrip()+"%"+" |/="+str(count).rstrip()+"%"+";"+str(warning)+";"+str(critical)+";"+str(min_wartosc)+";"+str(max_wartosc))
         os.remove(str(k))
         sys.exit(2)
      else:
         print("Ok - filesystem usage "+str(count).rstrip()+"%"+" |/="+str(count).rstrip()+"%"+";"+str(warning)+";"+str(critical)+";"+str(min_wartosc)+";"+str(max_wartosc))
         os.remove(str(k))
         sys.exit(0)
   elif os.path.isfile(str(k)) == False: #jesli pliku k nie wygenerowalo
      print ("Unknown - Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def fnCheckTemperature(srvname, warning):#funkcja pobiera prog warning ## 
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" \"ipmitool sunoem cli show\ /SYS/T_AMB |grep value | grep -Po '\d+.\d+\sdegree\sC' | grep -Po '^\d+'\" |cut -d ' ' -f2- > "+str(k))
   
   command.read()
   
   if os.path.isfile(str(k)) == True and os.stat(str(k)).st_size > 0: 
      f = open(str(k))
      count = f.read()
      try:
         int(count) >= int(warning)
         print("Warning : temperature "+str(count).rstrip()+"C")
      except:
         print ("Unknown: Wystapil problem z wykonaniem polecenia")
         os.remove(str(k))
         sys.exit(3)
      else:
         print("Ok: temperature "+str(count).rstrip()+"C")
         os.remove(str(k))
         sys.exit(0)
   elif os.path.isfile(str(k)) == False: #jesli pliku k nie ma wygenerowalo
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)
    
 
def fnStatusASMDisk(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e list griddisk attributes name, ASMDeactivationOutcome, ASMModeStatus | grep -v ONLINE |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnStatusStorageNodes(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e \"list metriccurrent attributes all where objectType = \'CELL\' \" |grep -v normal |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnStatusFlashDisks(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e \"list celldisk where disktype=flashdisk\" | grep -v normal |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnStatusFlashCache(cellname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(cellname)+" cellcli -e \"list flashcache detail\" |egrep \"status|size\" | grep -v \"normal\" | grep -v \"5.817901611328125T\" |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnStatusInfiniband(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" ibstatus | grep state | egrep -v '(LinkUp|ACIVE)' | grep -v \"4: ACTIVE\" |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnCheckInfiniband(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" /opt/oracle.SupportTools/ibdiagtools/verify-topology |sed '1d' |egrep -v '(SUCCESS|NOT APPLICABLE)' |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnCheckMemoryErrors(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" ipmitool sel list | grep PCI | cut -f1 -d : | sort -u |cut -d ' ' -f2- > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnCheckPSU(srvname):
   k1 = gen_tmp_file()
   k2 = gen_tmp_file()
   command1 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" 'ipmitool sunoem cli show\ /SYS/PS0 |grep fault_state |grep -v \"OK\"' > "+str(k1))
   command2 = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" 'ipmitool sunoem cli show\ /SYS/PS1 |grep fault_state |grep -v \"OK\"' > "+str(k2))
   command1.read()
   command2.read()
   
   if os.path.isfile(str(k1)) == True and os.path.isfile(str(k2)) == True: #jesli istnieje plik k1 i k2
      if os.stat(str(k1)).st_size == 0 and os.stat(str(k2)).st_size == 0: #jesli wygenerowany plik k1 i k2 jest pusty to jest OK
         print ("Ok : PS1 and PS0 are UP")
         os.remove(str(k1))
         os.remove(str(k2))
         sys.exit(0)
      elif os.stat(str(k1)).st_size > 0 and os.stat(str(k2)).st_size == 0: #jesli wygenerowany plik k1 cos zawiera
         print ("Warning : PS0 down")
         os.remove(str(k1))
         os.remove(str(k2))
         sys.exit(1)
      elif os.stat(str(k1)).st_size == 0 and os.stat(str(k2)).st_size > 0: #jesli wygenerowany plik k2 cos zawiera
         print ("Warning : PS1 down")
         os.remove(str(k1))
         os.remove(str(k2))
         sys.exit(1)
      elif os.stat(str(k1)).st_size > 0 and os.stat(str(k2)).st_size > 0: #jesli plik k1 i k2 cos zawiera
         print ("Critical : PS1 and PS2 are DOWN")
         os.remove(str(k1))
         os.remove(str(k2))
         sys.exit(2)	     
   elif os.path.isfile(str(k1)) == False and os.path.isfile(str(k2)) == False: #jesli nie wygenerowal sie k1 i k2
      print ("Unknown: Wystapil problem z wykonaniem polecenia")
      sys.exit(3)

def fnCheckILOMErrors(srvname):
   k = gen_tmp_file()
   command = os.popen("dcli -l "+str(username)+" -c "+str(srvname)+" 'ipmitool sunoem cli show\ faulty' |cut -d ' ' -f2- |egrep -v '(Property|-------------------|Connected|show faulty|^$|closed|Disconnected)' > "+str(k))
   command.read()
   set_nagios_status3(k)

def fnCheckPublicBond(): #do poprawy polecenie bashowe
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
      print ("Warning : cell_count: "+str(cell_count)+ " | flashe_cache_count: "+str(flash_cache_count))
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
