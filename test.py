import re

i = '#D7CEFF'

if re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', i):
	print('Y')
else:
	print('N')

print(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', i))