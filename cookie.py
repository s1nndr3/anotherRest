import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode

"""The session is first converted to a JSON string. 
The string of JSON is encrypted using the AES 256 standard which turns it into garbled bytes. 
It is then base64 encoded so it is an ASCII string, since the underlying HTTP protocols expect to work with ASCII. 
That base64 encoded string becomes the value of the cookie."""

def cookie_encode(raw_cookie, key):
		j = raw_cookie.encode("utf-8")

		cipher = AES.new(key, AES.MODE_CBC)
		ciper_text_b = cipher.encrypt(pad(j, AES.block_size))
		iv = cipher.iv
		cookie_encoded = b64encode(iv + ciper_text_b)
		return cookie_encoded

def cookie_decode(_input, key):
	try:
		inn = b64decode(_input)
		iv = inn[:AES.block_size]
		ct = inn[AES.block_size:]
		cipher = AES.new(key, AES.MODE_CBC, iv)
		pt = unpad(cipher.decrypt(ct), AES.block_size)
		return pt.decode("utf-8")
	except ValueError and KeyError:
		return None

def new_raw_cookie(session_id = "-1", acc_id = "-1", expires = "-1"):
	json_str = "{"
	json_str += f"\"session_id\": \"{session_id}\"" 
	json_str += f", \"acc_id\": \"{acc_id}\"" 
	json_str += f", \"expires\": \"{expires}\""
	json_str += "}"
	return json_str#json.loads(json_str)

def cookie_headder(cookie_encoded):
	if (cookie_encoded):
		return f"Set-Cookie: {cookie_encoded}; SameSite=Strict; Secure"
	else:
		return None