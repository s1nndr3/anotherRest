#Backend for "vehicle list" web application
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from rest import RestApi, Responce, Login
import json
import os
from base64 import b64encode

API = RestApi(port = 54387, host = "0.0.0.0")
log = Login()

@API.functionality("/", "GET")
@log.login_required()
def index(_id):
	return Responce("test", 200)

@API.functionality("/parking", "GET")
def index(_id):
	fp =  open("../Bed-2056-Project/parking_vs_weather.html", "rb")
	return Responce("", 200, text_type = "text/html", fp = fp)

@API.functionality("/data.zip", "GET")
def index(_id):
	add =  f"Content-Description: File Transfer"
	fp =  open("../Bed-2056-Project/data.zip", "rb")
	return Responce("", 200, headder_add = add, text_type = "application/zip", fp = fp)

if __name__ == "__main__":
	API.start()
