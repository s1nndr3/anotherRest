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
		return cookie_encoded.decode('utf-8')

def cookie_decode(_input, key) -> str:
	try:
		inn = b64decode(_input)
		iv = inn[:AES.block_size]
		ct = inn[AES.block_size:]
		cipher = AES.new(key, AES.MODE_CBC, iv)
		pt = unpad(cipher.decrypt(ct), AES.block_size)
		return pt.decode("utf-8")
	except ValueError and KeyError and TypeError:
		return ""

def new_raw_cookie(session_id = "-1", acc_id = "-1", expires = "-1", other = None):
	raw = {
		"session_id": session_id,
		"acc_id": acc_id,
		"expires": expires,
		"other": other
	}
	return json.dumps(raw)

def cookie_headder(cookie_encoded, max_age = 432000) -> str:
	if (cookie_encoded):
		return f"Set-Cookie: acc={cookie_encoded}; SameSite=Strict; Max-Age={max_age}; Secure=true"
	else:
		return ""