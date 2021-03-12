#Example code
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from rest import RestApi, Responce, Login

# If the rest api shuld use https include certificate and key like:
CERTIFICATE = {"CERTIFICATE": 'sertificate/selfsigned.crt', "PRIVATEKEY" : 'sertificate/selfsigned.key'}
API = RestApi(port = 8080, host = "0.0.0.0", cert = CERTIFICATE)

#initialize Login 
log = Login(b'\xc8\x0fmF\xc7\x14\xb8\x1c\x05\xd4\xbe|\xd3\t\x16\xa0')

# Example of simple endpoint.
@API.functionality("/", "GET")
def index(par):
	return Responce("Index", 200)

# Example of endpoint that requieres login.
@API.functionality("/login-required", "GET")
@log.login_required()
def login_required(par):
	return Responce("You are logged in :)", 200)

# Example of loggin inn a user. (Browser will need cookie support)
@API.functionality("/login", "GET")
def login(par):
	h = log.login(123, 1)
	return Responce("Logged in", 200, h)

# Example of logout
@API.functionality("/logout", "POST")
def logout(par):
	try:
		h = log.logout(par["cookie"])
	except Exception:
		return Responce("Not logged in", 401)
	return Responce("logged out", 200, h)

## par have the fields (is a dictionaries):
# 	* par["data"] (The all the data from the request)
# 	* par["body"] (The body from the request)
#	* par["request"] (The request i.e. everything after "?" in the url)
#	* par["id"] (If @log.login_required() is present this will hold the user id)
#	* self["cookie"] (The cookie; if there was one with the request)

# Start the API
if __name__ == "__main__":
	API.start()
