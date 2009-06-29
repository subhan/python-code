import threading,urllib
import socket,os
import sys,pprint
import settings
from subprocess import call

import cgi,cgitb

CRLF = "\r\n"


cgitb.enable()
form = cgi.FieldStorage()
def start_server(host,port):
	server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		server.bind((host,port))
	except:
		print "Address is already in use"
		port = input("Please Enter A New Port NO. : ")
		server.bind((host,port))
		
	server.listen(5)
	print "server started on %s : %s" %(host,port)

	try:
		while True:
			clientsocket,address = server.accept()
			t = threading.Thread(target=handler,args=(clientsocket,))
			t.run()
	except KeyboardInterrupt:
		print "server is shutting down"
		server.close()

class Request:
	def __init__(self,method,path,f):
		self.method = method
		self.path = path
		self.client = f
		self.data = ""
		self.headers = {}

	def process(self):
		if self.method == "GET":
			self.processGetRequest()
		elif self.method == "POST":
			self.processPostRequest()
		response = Response()
		response.data = self.data
		response.headers = self.headers
		return response

	
	def processGetRequest(self):
		if not hasattr(settings,'SCRIPTALIAS'):
			self.execCgi()
		else:
			self.data = """
			<html>
				<head><title>python webserver</title></head>
			<body>
				<form method="POST" action="index.cgi">
					<input name='name' type='text'></br>
					<input type='submit' value='Add'>
				</form>
			</body>
			</htm>
			"""
	
	def processPostRequest(self):
		if hasattr(settings,'SCRIPTALIAS'):
			pass
			#self.execCgi()
		#self.headers['Content-type'] = "text/html"
		#self.data = self.path

def execCgi(path,f):
	scriptPath = getattr(settings,'SCRIPTALIAS')	
	outfile = open('/tmp/out.txt','w')
	if '?' in path:
		index = path.index('?')
		file = path[1:index]
		fullCgiPath = os.path.abspath(os.path.join(scriptPath,file))
		if os.path.exists(fullCgiPath):
			call([fullCgiPath,path[index+1:]],stdout=outfile)
	else:
		fullCgiPath = os.path.abspath(os.path.join(scriptPath,path[1:].strip()))
		d = dict([(field,form.getvalue(field,'')) for field in form.keys()])
		args=""
		print d,fullCgiPath
		call([fullCgiPath],stdout=outfile)
	outfile.close()	
	data = open('/tmp/out.txt').readlines()
	k,v= data[0].strip().split(":")
	res = Response()
	res.headers[k.strip()] = v.strip()
	res.data = "".join(data[1:])
	res.send(f)
	f.close()
	return 


class Response:
	def __init__(self):
		self.http_version = "HTTP/1.1"
		self.status = "200 OK"
		self.headers = {}
		self.data = ""

	def send(self,f):
		self.headers['Content-Length'] = len(self.data)
		f.write("%s:%s\r\n" %(self.http_version,self.status))
		header_string = CRLF.join(["%s:%s" %(k,v) for k,v in self.headers.items()])
		f.write(header_string)
		f.write(CRLF)
		f.write(CRLF)
		f.write(self.data)
		f.close()
		

class WriteObject:
	def __init__(self):
		self.content=[]
	def write(self,string):
		self.content.append(string)


def handler(client):
	cgitb.enable()
	form = cgi.FieldStorage()
	f = client.makefile()
	method,path,headers = read_headers(f)
	print method,path
	pprint.pprint(headers)
	if hasattr(settings,'SCRIPTALIAS'):
		execCgi(path,f)
	else:
		request = Request(method,path,f)
		response = request.process()
		response.send(f)
		client.close()
	return 


def read_headers(f):
	method,path,version = f.readline().split()
	headers = {}
	
	while True:
		data = f.readline()
		if data.strip() == "":
			break
		k,v = data.strip().split(":",1)
		headers[k.strip()] = v.strip()

	return method,path,headers	


if __name__ == "__main__":
	
	if hasattr(settings,'PORT'):
		port = getattr(settings,'PORT')	
	elif len(sys.argv) == 2:
		port = int(sys.argv[1])
	else:
		port = 8080

	start_server('localhost',port)
	
