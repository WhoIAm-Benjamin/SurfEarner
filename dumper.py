import pickle

try:
	with open('settings.txt', 'rb') as f:
		s = pickle.load(f)
		login, password, timeout = s.split('\n')
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
with open('settings.txt', 'wb') as f:
	s = 'LOGIN:{}\nPASSWORD:{}\nTIMEOUT:{}'.format(login, password, timeout)
	pickle.dump(s, f)