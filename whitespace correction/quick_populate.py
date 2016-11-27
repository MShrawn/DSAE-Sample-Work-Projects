import os

def formal(x):
	if x<10:
		return "00"+str(x);
	elif x<100:
		return "0"+str(x);
	else:
		return str(x);

for i in range(1,227):
	os.makedirs(formal(i));
