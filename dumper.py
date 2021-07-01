import pyAesCrypt
from os.path import splitext
from os import remove

def main():
	try:
		file = 'settings.txt.crp'
		password_file = 'filepasswdroot'
		buffer_size = 512 * 1024
		try:
			pyAesCrypt.decryptFile(file, str(splitext(file)[0]), password_file, buffer_size)
		except ValueError:
			raise FileNotFoundError
		with open('settings.txt', 'r') as f:
			login, password, timeout = f.readlines()
		login = login.split(':')[1].strip('\n')
		password = password.split(':')[1].strip('\n')
		timeout = timeout.split(':')[1].strip('\n')
		change = input('What are you want to change?\n').lower()
		if change == 'login':
			login = input('Enter new login: ')
		elif change == 'password':
			password = input('Enter new password: ')
		elif change == 'timeout':
			timeout = input('Enter new timeout: ')
	except FileNotFoundError:
		login = input('Enter login: ')
		password = input('Enter password: ')
		timeout = input('Enter timeout: ')
	finally:
		file = 'settings.txt'
		s = 'LOGIN:{}\nPASSWORD:{}\nTIMEOUT:{}'.format(login, password, timeout)
		with open('settings.txt', 'w') as f:
			f.write(s)
		pyAesCrypt.encryptFile(str(file), str(file) + '.crp', password_file, buffer_size)
		remove(file)

main()
