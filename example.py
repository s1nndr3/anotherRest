#Backend for "vehicle list" web application
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from rest import RestApi, Responce, Login

# If the rest api shuld use https include certificate and key like:
CERTIFICATE = {"CERTIFICATE": 'sertificate/fullchain.pem', "PRIVATEKEY" : 'sertificate/privkey.pem'}
API = RestApi(port = 54387, host = "0.0.0.0", cert = CERTIFICATE)

#initialize Login 
log = Login()

@API.functionality("/", "GET")
@log.login_required()
def index(_id):
	return Responce("test", 200)

if __name__ == "__main__":
	API.start()
