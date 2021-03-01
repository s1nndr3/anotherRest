# webserver
Note. work in progress ***Do not use for critical work or sensetive data.***

***Python3*** implementation of a multithreaded rest-API that can use either Http or Https.

### This implementation provides:
- Easy to use syntax for implementing a rest-API. (see example.py)
- Cookie support.
- Simple Login system.

### Required packages:
- pandas
- Crypto
- pycrypto
- pycryptodome

#### Disclaimer:
- Inspiration for the syntax is taken from Flask "https://flask.palletsprojects.com/en/1.1.x/". But this is a brand new implementation and have no connection to ether the Flask tam or implementation.

#### Other important notes:
- ***Do not*** use the certificate in the certificate folder, It is only for demonstration purposes.
- The provided login and cookie support is not finished or properly tested and may have security bugs in them.

Stop with: CTRL+c