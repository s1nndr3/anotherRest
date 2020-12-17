from datetime import datetime

class Loging:
	def __init__(self):
		self.log_file = "log.txt"

	def log_entry(self, string: str, end = "\n"):
		with open(self.log_file, "a+") as fp:
			fp.write(f"{datetime.now()} - {string}{end}")
			fp.close()