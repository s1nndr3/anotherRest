#test for rest api 

import pytest
import http.client
import ssl
import json
from rest import str_partition

"""Server"""
server = "127.0.0.1"
port = 8080

"""acc/login credentials:"""
_id = 1
name = "qwe"
email = "test@test.test"
password = "\\x24326224313224626c526a6f7777315962646234545971555343597175307944344a5932486d5171625a2e45656d5350573558676b743034515a6543"


"""Request method all the test use for comunication with the server"""
def request(method, path, body=None, headers=None):

	context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	context.verify_mode = ssl.CERT_NONE #do not check serificate (just for testing)

	conn = http.client.HTTPSConnection(server, port, context=context)
	conn.request(method, path, body=body, headers=headers)
	response = conn.getresponse()
	status = response.status
	data = response.read()
	cookie = response.getheader("Set-Cookie") ##get cookie header as str
	response.close()
	conn.close()
	return status, data, cookie

"""Test session varables"""
session_cookie = None



"""Create a new account, shuld try to use same email two times"""
def test_new_account():
	pass

"""Test for login, shuld use wrong credentials first time"""
def test_login():
	method = 'POST'
	path = '/login'

	payload_raw = {"email": email, "password": password}
	payload = json.dumps(payload_raw)

	#print(len(payload))

	headers = {"Content-type": "application/json", "Content-Length": len(payload)}

	status, data, cookie = request(method, path, body=payload, headers=headers)

	if (not cookie or status != 20):
		pytest.fail(f"LOGIN error!!!, status: {status}")

	session_cookie = str_partition(cookie, end=";")
	print(f"status: {status} \ndata: {data} \ncookie: {session_cookie}")

	return 1

"""Test collection for parts"""
def test_new_part():
	pass #not yet implemented

def test_edit_part():
	pass #not yet implemented

def test_remove_part():
	pass #not yet implemented


"""Logout and remove test account"""
def test_logout():
	pass #not yet implemented

def test_remove_account():
	pass #not yet implemented
