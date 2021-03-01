#Backend for "vehicle list" web application
#Version: 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

from rest import RestApi, Responce, Login
import json
import os
from base64 import b64encode
from psql import Psql

API = RestApi(port = 54387, host = "0.0.0.0")
log = Login()
db = Psql()

data_loc = "../websites/html-css/.data/"
website_loc = "../websites/html-css/"

@API.functionality("/", "GET")
def index(par):
	fp = open("../websites/html-css/template.html", "rb")
	return Responce("", 200, text_type = "text/html", fp = fp)

@API.functionality("/login", "POST")
def login(par):
	j = json.loads(par.data)
	u = j["uname"]
	p = j["psw"]

	query = "SELECT * FROM account WHERE email=%s"
	res = db.fetchone(query, u)
	print(res)

	if res and res[3] == p:
		h = log.login(res[0], 1)
		return Responce("login", 200, h)
	
	return Responce("Email or password incorrect", 401)

@API.functionality("/logout", "POST")
def logout(par):
	try:
		h = log.logout(par.cookie)
	except Exception:
		return Responce("Not logged in", 401)
	return Responce("logged out", 200, h)

@API.functionality("/veryfylogin", "POST")
def veryfy(par):
	v = True if log.is_loggedin(par.cookie) else False
	print(v)
	return Responce(f"{v}", 200)

@API.functionality("/.dash.html", "GET")
@log.login_required()
def dash(_id):
	fp =  open("../websites/html-css/.dash.html", "rb")
	return Responce("", 200, text_type = "text/html", fp = fp)

@API.functionality("/.dash.js", "GET")
@log.login_required()
def dash(_id):
	fp =  open("../websites/html-css/.dash.js", "rb")
	return Responce("", 200, text_type = "text/javascript", fp = fp)

@API.functionality("/.dash.css", "GET")
@log.login_required()
def dash(_id):
	fp =  open("../websites/html-css/.dash.css", "rb")
	return Responce("", 200, text_type = "text/css", fp = fp)

@API.functionality("/info", "GET")
@log.login_required()
def info(_id):
	info = {"nr-visitors":1}
	return Responce(json.dumps(info), 200)

@API.functionality("/parking", "GET")
def parking(par):
	fp =  open("../Bed-2056-Project/parking_vs_weather.html", "rb")
	return Responce("", 200, text_type = "text/html", fp = fp)

@API.functionality("/data.zip", "GET")
def data(par):
	add =  f"Content-Description: File Transfer"
	fp =  open("../Bed-2056-Project/data.zip", "rb")
	return Responce("", 200, headder_add = add, text_type = "application/zip", fp = fp)

@API.functionality("/new_post", "POST")
@log.login_required()
def new_post(par):
	j = json.loads(par.data)
	text = j["text"]
	print(text)
	
	if not text:
		return Responce("no content!", 400)

	query = "INSERT INTO post (date_time, post_text) VALUES (CURRENT_TIMESTAMP, %s) RETURNING id"
	_id = db.fetchone(query, text)[0]

	query = "INSERT INTO account_post (account_id, post_id) VALUES (%s, %s)"
	val = par.id, _id
	db.execute(query, *val)

	return Responce("Created", 201)

@API.functionality("/get_posts", "GET")
def get_posts(par):
	try:
		off, nr = par.request.split("-")
		off, nr = int(off), int(nr)
	except ValueError:
		return Responce("Unable to understand request!!!", 400)

	query = f"SELECT * FROM post ORDER BY date_time DESC OFFSET {off} limit {nr}"
	res = db.fetchall(query)
	#print(res)
	ret = []
	for r in res:
		d = {
			"date": str(r[1]), 
			"text": str(r[2])
			}
		ret.append(json.dumps(d))
	#print(', '.join(ret))
	#print(str(ret))
	return Responce("[" + ', '.join(ret) + "]", 200)


API.multiple(website_loc)

if __name__ == "__main__":
	API.start()
