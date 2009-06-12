import threading
import socket,os
import sys,pprint
import settings
from subprocess import call

CRLF = "\r\n"



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

	def execCgi(self):
		writer = WriteObject()
		sys.stdout = writer
		scriptPath = getattr(settings,'SCRIPTALIAS')	
		if '?' in self.path:
			index = self.path.index('?')
			args = self.path[index:]
			file = self.path[1:index]
			fullCgiPath = os.path.abspath(os.path.join(scriptPath,file))
			if os.path.exists(fullCgiPath):
				#code = call([fullCgiPath,args])
				sys.argv = args
		else:
			fullCgiPath = os.path.abspath(os.path.join(scriptPath,self.path[1:]))
			#data = open(fullCgiPath).read()
			exec open(fullCgiPath)
			#code = call([fullCgiPath])

		sys.stdout = sys.__stdout__
		self.data = "".join(writer.content)
		print "data : %s" %self.data
		self.headers['Content-type'] = "text/html"

	def processGetRequest(self):
		if hasattr(settings,'SCRIPTALIAS'):
			self.execCgi()
		else:
			self.data = """
			<html>
				<head><title>python webserver</title></head>
			<body>
				<p>Get Method</p>
			</body>
			</htm>
			"""
	
	def processPostRequest(self):
		pass	


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
		

class WriteObject:
	def __init__(self):
		self.content=[]
	def write(self,string):
		self.content.append(string)


def handler(client):
	f = client.makefile()
	method,path,headers = read_headers(f)
	pprint.pprint(headers)
	request = Request(method,path,f)
	response = request.process()
	response.send(f)
	client.close()



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

	writer = WriteObject()
	sys.stdout = writer
	start_server('localhost',port)
	
