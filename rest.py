#REST API
#Version: 0.0.2 March 2021
#By Sindre Sønvisen sindre@sundvis.net

from socket import socket, SOCK_STREAM, AF_INET
import threading as th
import time
import ssl
import os
import sys

if __package__:
	from .log import Loging
	from .cookie import *
	from .httpstatus import get_status
else:
	from log import Loging
	from cookie import *
	from httpstatus import get_status

class RestApi(Loging):
	def __init__(self, port = 8080, host = "localhost", cert = None, log_file = "connection_log.txt", allow_origin : list = [], http_redirect : bool = False):
		self.port = port
		self.host = host
		self.allow_origin = allow_origin # Access-Control-Allow-Origin header
		self.http_redirect = http_redirect
		
		self.func = []
		self.log_file = log_file

		self.work_pool = []
		self.work_queue = work_list()

		#Create socket
		self._setup_socket(cert)
		
	def _setup_socket(self, cert = None):
		self.socket = socket(AF_INET, SOCK_STREAM)#socket setup
		while(True):
			try:
				self.socket.bind((self.host, self.port))
				break
			except OSError as error:
				print("feiled when binding!! OSError")
				time.sleep(0.5)

		self.socket.listen()

		#Wrap socket to Https
		if cert:
			context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			context.load_cert_chain(cert["CERTIFICATE"],cert["PRIVATEKEY"])
			self.wrapped_socket = context.wrap_socket(self.socket, server_side=True)
		else:
			self.wrapped_socket = self.socket

	""" Call this when user want to start the server """
	def start(self, n = 3):
		for i in range(0, n):
			t = th.Thread(target=worker, args=(self, self.work_queue, i, self.func))
			t.start()
			self.work_pool.append(t)

		print("Worker(s) startup complete!")
		self._connect()
 	
		self._stop()


	""" Internal function to receive connections
		- Receive connection
		- Put connection on the work queue """
	def _connect(self):
		while(True):
			try:
				conn, addr = self.wrapped_socket.accept()# accept conection
			except OSError as error:
				print(f"feiled!! OSError")
				print(error)
				continue
			except KeyboardInterrupt: # Not ideal, should use signal
				break
			except:
				print("Unexpected error!", sys.exc_info()[0])
				continue

			self.work_queue.put({"conn": conn, "addr": addr})

	""" Internal function to stop
		- Send stop code (-1) to all workers
		- Join all workers 
		- close socket(s) """
	def _stop(self):
		for p in self.work_pool:
			self.work_queue.put(-1)

		for p in self.work_pool:
			p.join()

		self.wrapped_socket.close()
		self.socket.close()

		print("Shut down success")

	""" The function is stored in a list with goresponding route and methodwhen using:
	@RestApi.functionality("arg1", "arg2")
	def function(par):
		...Do someting... 
	"""
	def functionality(self, url, method):
		def decorator(original_func):

			#never used
			def wrapper():
				print("Wrapper test")

			#inser func in list
			self.func.insert(0, [url, method, original_func])

			return wrapper
		return decorator

	""" Only used internally by the multiple function"""
	def _makefunction(self, loc:str, file:str, pre:str):
		@self.functionality(f"{pre}/{file}", "GET")
		def func(par):
			fp = open(f"{loc}/{file}", "rb")
			mime = file.split(".")[1]
			mime = "javascript" if mime == "js" else mime
			return Responce("", 200, text_type = "text/"+mime, fp = fp)


	""" Add souport to get multiple files in a folder
	Use a "." in the beggining to ignore files or folders """
	def multiple(self, loc, pre = ""):
		files = os.listdir(loc)
		for f in files:
			if f[0] == ".":
				continue
			if(os.path.isdir(loc + f)):
				self.multiple(f"{loc + f}/", pre+"/"+f)
				continue

			self._makefunction(str(loc), str(f), str(pre))
			print(f"made: {pre}/{f}")

	def Responce(self, origin, *args, **kwargs):
		if self.allow_origin and origin in self.allow_origin:
			allow = [f"Access-Control-Allow-Origin: {origin}"]
			kwargs["header_add"] = allow if "header_add" not in kwargs else kwargs["header_add"] + allow
		return Responce(*args, **kwargs)


""" Response function """
def Responce(data: str, code: int, header_add: list[str] = [], text_type = "text/plain", fp = None):
	status = get_status(code)

	file_size = 0 if not fp else os.path.getsize(fp.name)

	header = f"HTTP/1.1 {code}  {status}\r\n"
	header += f"Content-Type: {text_type}; charset=utf-8\r\n"
	header += f"Content-Length: {len(data)+file_size}\r\n"
	header += "Access-Control-Allow-Credentials: true\r\n"

	header = header if len(header_add) == 0 else header + "\r\n".join(header_add) + "\r\n"

	header += "\r\n"

	responce = header + data
	
	return [responce, fp]


""" Thread safe list 
	- FIFO """
class work_list():
	def __init__(self):
		self.list = []
		self.lock = th.Lock()
		self.cond_v = th.Condition(lock=self.lock)

	""" Put value at the beginning """
	def put(self, val, timeout = -1):
		if not (self.cond_v.acquire(blocking=True, timeout=timeout)):
			return False
		self.list.insert(0, val)
		self.cond_v.notify(n=1)
		self.cond_v.release()

	""" Pop from the end"""
	def get(self, timeout = -1):
		while(True):
			if not (self.cond_v.acquire(blocking=True, timeout=timeout)):
				return False
			if (len(self.list) > 0):
				val = self.list.pop()
				self.cond_v.release()
				return val
			else:
				out = None if timeout == -1 else timeout
				if not (self.cond_v.wait(timeout=out)):
					self.cond_v.release()
					return False
				self.cond_v.release()

	""" Empthy the list """
	def delete(self, timeout = -1):
		if not (self.cond_v.acquire(blocking=True, timeout=timeout)):
			return False
		print("delete from list:")
		while len(self.list) > 0:
			print(f"    {self.list.pop()}")
		self.cond_v.release()

""" Thread worker
	- wait on something to handle
	- -1 is exit code """
def worker(API, queue, _id, funcs):
	print(f"Hello from process {_id}")
	while(True):
		c = queue.get()
		if(c == -1):
			return
		conn = c["conn"]
		addr = c["addr"]
		_handle(API, conn, addr, funcs)


""" Function that handles each request
	- Note. Started by multiple threads simultaneously"""
def _handle(API, conn, addr, funcs):
	ip_addr = str_partition(str(addr), ("('"), ("',"))

	"""Retrive raw data"""
	try:
		data_raw = conn.recv(1024)
		#print(data)
	except ssl.SSLError as error:
		print(f"ssl error when reciving data {error}")
		return
	except ConnectionResetError as error:
		print(f"ConnectionResetError error when reciving data: {error}")
		return

	if not data_raw:
		return

	body = header = ""
	"""split in to header and body, and decode header"""
	def get_header(raw):
		try:
			header, body = raw.split(b"\r\n\r\n", 1)
		except ValueError:
			data_raw = conn.recv(1024)
			return get_header(raw+data_raw)
			""" header = data_raw.split(b"\r\n\r\n", 1)[0]
			body = None """
		return header.decode('utf-8'), body, raw

	try:
		header, body, data_raw = get_header(data_raw)
	except Exception as error:
		print(f"error in get_header: {error}")

	try:
		cookie = {f"{C.split('=',1)[0]}":f"{C.split('=',1)[1]}" for C in header.split("Cookie: ")[1].split("\n")[0].split("; ")}
	except IndexError:
		cookie = {"acc":None} #No cookie
	
	try:
		content_len = int(str_partition(header, ("Content-Length: "), ("\r\n")))
	except TypeError:
		content_len = 0
	except ValueError:
		content_len = 0

	received = (0 if not body else len(body))
	if content_len > received:
		rest_len = content_len - received
		rest = b''
		while rest_len > 0:
			try:
				rest += conn.recv(1024)
				rest_len -= 1024
			except  ssl.SSLError as error:
				print(f"ssl error when reciving data {error}")
				return
			except ConnectionResetError as error:
				print(f"ConnectionResetError error when reciving rest of data: {error}")
				return

		body = rest if not body else body + rest

	"""Find method, url/path and request"""
	method = str_partition(header, None, (" "))
	url = str_partition(header, (" "), (" "))
	host = str_partition(header, ("Host: "), ("\r\n"))
	origin = str_partition(header, ("Origin: "), ("\r\n"))
	content_type = str_partition(header, ("Content-Type: "), ("\r\n"))

	path, request, *_ = url.split("?") + [None]

	func_entry = [x for x in funcs if x[0] == path and x[1] == method]
	print(func_entry)

	par = {
		"cookie": cookie,
		"data": data_raw,
		"body": body,
		"request": request,
		"id": None,
		"host": host,
		"origin": origin,
		"content_type": content_type
	}

	"""Call correct function and get back a responce"""
	responce = None
	if(len(func_entry) > 0):
		func_entry = func_entry[0]
		try:
			responce = func_entry[2](par)
		except Exception as e:
			print(f"Exception in endpoint: {e}")
			responce = API.Responce(origin, "error", 400)
	elif(method == "OPTIONS"):
		methods = [x[1] for x in funcs if x[0] == path]
		header = ["Access-Control-Allow-Methods: OPTIONS, " + ", ".join(methods), "Access-Control-Allow-Headers: Authorization, Content-Type"]
		responce = API.Responce(origin, "", 200, header_add=header)
	else:
		print(f"Error: Endpoint {path} method {method} do not exist!!!!")
		responce = API.Responce(origin, "Endpoint do not exist", 404)
	if not responce:
		responce = API.Responce(origin, "Server error", 500)

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

def str_partition(str, start = None, end = None) -> str  :
	ret = str

	if (start != None):
		try:
			ret = ret.split(start)[1]
		except IndexError:
			return ""

	if (end != None):
		try:
			ret = ret.split(end)[0]
		except IndexError:
			return ""
	return ret


"""Login class"""
class Login():
	def __init__(self, AES_key = None):
		self.AES_key = AES_key if AES_key else get_random_bytes(16)
		print(self.AES_key)

	def login(self, acc_id:int, expires:int, other = None, domain="") -> list[str]:
		raw = new_raw_cookie(acc_id=str(acc_id), expires=str(expires), other=other)
		headder = cookie_headder(cookie_encode(raw, self.AES_key), domain=domain)
		return [headder] if headder != "" else []

	def logout(self, cookie, domain):
		if not self.is_loggedin(cookie):
			raise Exception("Was not logged in")

		header = cookie_headder("deleted", 0, domain=domain)
		return [header] if header != "" else []

	def is_loggedin(self, cookie):
		if(not cookie):
			return None
		raw = cookie_decode(cookie, self.AES_key)
		return json.loads(raw)

	def login_required(self, veryfy = None):
		def decorator(func):
			def wrapper(par):
				j = self.is_loggedin(par["cookie"]["acc"])
				if (j == None):
					return Responce("Unauthorized", 401)
				if callable(veryfy) and not veryfy(j):
					return Responce("Unauthorized", 401)
				par["id"] = j["acc_id"]
				return func(par)
			return wrapper
		return decorator


if __name__ == "__main__":
	pass


