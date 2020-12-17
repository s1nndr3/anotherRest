#Backend for "vehicle list" web application
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from rest import RestApi, Responce, Login
import json
import os
from base64 import b64encode

API = RestApi(port = 54387, host = "0.0.0.0")
log = Login()

file = open('../Bed-2056-Project/parking_vs_weather.html',mode='r')
parking = file.read()
file.close()

@API.functionality("/", "GET")
@log.login_required()
def index(_id):
	return Responce("test", 200)

@API.functionality("/parking", "GET")
def index(_id):
	return Responce(parking, 200, text_type = "text/html")

@API.functionality("/update-parking", "POST")
def index(_id):
	global parking 
	file = open('../Bed-2056-Project/parking_vs_weather.html',mode='r')
	parking = file.read()
	file.close()
	return Responce("Success", 200)

if __name__ == "__main__":
	API.start()
