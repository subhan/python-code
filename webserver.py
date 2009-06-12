import threading
import socket
import sys,pprint

CRLF = "\r\n"

def start_server(host,port):
	server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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
		


def handler(client):
	f = client.makefile()
	method,path,headers = read_headers(f)
	pprint.pprint(headers)
	
	response = Response()

	if method == "GET":
		response_get(path,f,response)

	elif method == "POST":
		response_post(path,f,response)

	client.close()


def response_get(path,f,response):
	mesg = """
	<html>
		<head><title>python webserver</title></head>
	<body>
		<p>Get Method</p>
	</body>
	</htm>
	"""
	response.data = mesg
	response.headers['Content-Type'] = "text/html"
	response.send(f)
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
	
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	else:
		port = 8080

	start_server('localhost',port)
	
