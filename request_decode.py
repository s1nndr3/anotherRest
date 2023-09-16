
hex = {
"%7B" : "{",
"%7D" : "}",
"%22" : "\"",
"%5B" : "[",
"%5D" : "]",
"%20" : " ",
"%40" : "@",
"%3D" : "=",
"%2F": "/",
"%2B": "+",
"%28" : "(",
"%29" : ")",
"%3C" : "<",
"%3E" : ">",
"%2C" : ",",
"%3B" : ";",
"%3A" : ":",
"%3F" : "?"
}


def decode(_str):
	if _str == "":
		return ""
	elif _str[0] == "%":
		n = hex[_str[:3]]
		return decode(n + _str[3:])
	else:
		return _str[0] + decode(_str[1:])

# function to return key for any value
def get_key(v):
	for key, value in hex.items():
		if value == v:
			return key
	return None

def encode(_str):
	if _str == "":
		return ""

	key = get_key(_str[0])
	if key:
		return key + encode(_str[1:])
	else:
		return _str[0] + encode(_str[1:])

	

if __name__ == "__main__":
	t = "%7B%22e-mail%22:%22pytest%40test.py%22%7D"
	print(t)
	d = decode(t)
	print(d)
	e = encode(d)
	print(e)
	print(e == t)