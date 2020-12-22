#REST API
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from socket import *
import threading
import time
import ssl
from enum import Enum
import json
import pandas as pa
from log import Loging
import os
from cookie import *


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('sertificate/fullchain.pem','sertificate/privkey.pem')

AES_key = b'\xa06\xf5\xb5J)\xb9\x02\xa4K\x97\xc6\x94\x8b\xea%' #get_random_bytes(16) #used for cookie
print(AES_key)

#Used in the response function
http_code_csv = "http_status.csv"
http_code = pa.read_csv(http_code_csv, sep=",", comment='#')


class RestApi(Loging):
	def __init__(self, port = None, host = None):
		self.port = 8080 if not port else port
		self.host = "localhost" if not host else host
		self.conn_list = []
		self.func = []
		self.log_file = "connection_log.txt"

		self.socket = socket(AF_INET, SOCK_STREAM)#socket setup
		while(True):
			try:
				self.socket.bind((self.host, self.port))
				break
			except OSError as error:
				print("feiled when binding!! OSError")
				time.sleep(0.5)

		self.socket.listen()
		#use when updating to https!!!
		self.wrapped_socket = context.wrap_socket(self.socket, server_side=True)

	def start(self):
		self.conn_lock = threading.Lock()
		self.conn_cond_v = threading.Condition(lock=self.conn_lock)

		connect = threading.Thread(target=self.connect, args=())
		handle = threading.Thread(target=self.handle_start, args=())

		connect.start()
		handle.start()
		print("Startup complete!")
		self.log_entry("Startup complete!")
		print(f"the server ({self.host}) is listening on port {self.port}")
		#print("Functions: \n", self.func)

		#self.stop()
		connect.join()
		handle.join()
		self.stop()

	def connect(self):
		while(True):
			#print(self.conn_list)
			try:
				conn, addr = self.wrapped_socket.accept()#accept conection
			except OSError as error:
				print("feiled!! OSError")
				print(error)
				continue
			
			#print(f"Connection from: {addr}")
			self.conn_cond_v.acquire(blocking=True, timeout=-1)
			self.conn_list.insert(0, [conn, addr])
			#print("LIST LEN = ", len(self.conn_list))
			self.conn_cond_v.notify(n=1)
			self.conn_cond_v.release()
			#print(f"Connection by {addr} inserted to list")


	def handle_start(self):
		while (True):
			self.conn_cond_v.acquire(blocking=True, timeout=-1)
			if (len(self.conn_list) > 0):
				conn, addr = self.conn_list.pop()
				self.conn_cond_v.release()

				conn_h = threading.Thread(target=handle, args=(conn, addr, self.func, self.log_entry))
				conn_h.start()

			else:
				self.conn_cond_v.wait(timeout=None) #wait for more conections
				self.conn_cond_v.release()

	def stop(self):
		socket(AF_INET, SOCK_STREAM).connect( (self.host, self.port))
		self.wrapped_socket.close()
		self.socket.close()

	# The function is stored in a list with goresponding route and methodwhen using: 
	#@RestApi.functionality("arg1", "arg2")
	#def function():
	#	"""Do someting"""
	def functionality(self, url, method):
		def decorator(original_func):

			#never used
			def wrapper():
				print("Wrapper test")

			#inser func in list
			self.func.insert(0, [url, method, original_func])

			return wrapper
		return decorator

def pars_url(url):
	path = str_partition(url, end = "?")
	request = str_partition(url, start = "?")
	r = []
	while request:
		print(request)
		r.append(str_partition(request, end = "&"))
		request = str_partition(request, start = "&")

	return path, r
	


def handle(conn, addr, funcs, logfunc):
	ip_addr = str_partition(str(addr), ("('"), ("',"))

	"""Retrive raw data"""
	try:
		data = conn.recv(1024)
		#print(data)
	except ssl.SSLError as error:
		print(f"ssl error when reciving data {error}")
		return

	if not data:
		return

	"""Decode data and split in to header and body"""
	data = data.strip().decode('utf-8')
	header = str_partition(data, None, "\r\n\r\n")
	body = str_partition(data, "\r\n\r\n", None)

	cookie = str_partition(header, "Cookie: ", "\n")#Selecting just the first
	if(cookie):
		cookie = cookie[2:].encode()#not pretty, but it works


	""" print("\nheader: \n", header)
	print("\nbody: \n", body) """

	"""Find method and url"""
	method = str_partition(header, None, (" "))
	url = str_partition(header, (" "), (" "))
	path, request = pars_url(url)
	print(f"addr: {addr} Path: {path} args: {request}")
	logfunc(f"addr: {addr} Path: {path} nargs: {request}")
	func_entry = [x for x in funcs if x[0] == url and x[1] == method]

	par = args()
	par.cookie = cookie
	par.data = body
	par.request = None

	"""Call correct function and get back a responce"""
	responce = None
	if(len(func_entry) > 0):
		func_entry = func_entry[0]
		try:
			if (func_entry[1] == "POST"):
				responce = func_entry[2](body)
			else:
				responce = func_entry[2](par)
		except Exception as error:
			responce = Responce(error, 400)
	else:
		print("Error: Endpoint do not exist!!!!")
		responce = Responce("Endpoint do not exist", 404)
	if not responce:
		responce = Responce("Server error", 500)

	"""Send responce and close conection"""
	#if type(responce) == tuple:
	conn.send(responce[0].encode('utf-8'))
	while responce[1]:
		l = responce[1].read(1024)
		if not l:
			responce[1].close()
			break
		conn.send(l)
	conn.close()

class args():
	def __init__(self):
		self.cookie = None
		self.data = None
		self.request = None



def str_partition(str, start = None, end = None):
	ret = str

	if (start != None):
		try:
			ret = ret.split(start)[1]
		except IndexError:
			return None

	if (end != None):
		try:
			ret = ret.split(end)[0]
		except IndexError:
			return None
	return ret

def Responce(data: str, code: int, headder_add = None, text_type = "text/plain", fp = None):
	row = (http_code.loc[http_code["status"] == code])
	status = row["status_description"].values[0] #haha

	file_size = 0 if not fp else os.path.getsize(fp.name)

	headder = f"HTTP/1.1 {code}  {status}\r\n"
	headder += f"Content-Type: {text_type}; charset=utf-8\r\n"
	headder += f"Content-Length: {len(data)+file_size}\r\n"
	if(headder_add):
		headder += f"{headder_add}\r\n"
	headder += "\r\n"

	responce = headder + data
	
	#print(responce)
	return [responce, fp]


"""Login class"""
class Login():
	def __init__(self):
		#self.logged_list = []
		pass

	def login(self, acc_id, expires):
		raw = new_raw_cookie(acc_id=acc_id, expires=expires)
		headder = cookie_headder(cookie_encode(raw, AES_key))
		return headder

		#self.logged_list.insert(0, (cookie, acc_id, acc_type))

	def logout(self, cookie):
		#self.logged_list = [x for x in self.logged_list if x[0] != cookie]
		pass

	def is_loggedin(self, cookie):
		if(not cookie):
			return None

		raw = cookie_decode(cookie, AES_key)
		print(raw)
		return raw

	def login_required(self, r_type = None):
		def decorator(func):
			def wrapper(cookie):
				print("wraper test", r_type, cookie)
				_id = self.is_loggedin(cookie)
				if (_id == None):
					return Responce("Unauthorized", 401)
				return func(_id)
			return wrapper
		return decorator


if __name__ == "__main__":
	#API = RestApi()
	#API.start()
	test = cookie(1, 1)
	t = test.encode(AES_key)
	print(t)
	t2 = test.decode(t, AES_key)
	print(t2)


