#Backend for "vehicle list" web application
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from rest import RestApi, Responce, Login
from psql import Psql, UniqueViolation
import json
import os
from base64 import b64encode
import bcrypt

API = RestApi()
log = Login()
db = Psql()

@API.functionality("/", "GET")
@log.login_required()
def index(_id):
	return Responce("test", 200)

if __name__ == "__main__":
	API.start()
