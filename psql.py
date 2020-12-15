#Handler for postgreSQL
#Version 0.0.1 July 2020
#By Sindre Sønvisen sindre@sundvis.net

import psycopg2

UniqueViolation = psycopg2.errors.lookup('23505')
ForeignKeyViolation = psycopg2.errors.lookup('23503')

#Plan to fix not duplicate code with cursors
def decorator(func):
	def wrapper(*args, **kwargs):
		print("before")
		func(*args, **kwargs)
		print("after")
	return wrapper

class Psql():
	def __init__(self):
		#Open connection
		self.conn = psycopg2.connect(
			host = "localhost",
			database = "vehicle_data",
			user = "vehicle",
			password = "vehicle-list",
			port = 5432 
		)

	def new_cursor(self):
		return self.conn.cursor()

	def fetchall(self, query, *values):
		cur = self.new_cursor()
		cur.execute(query, vars = values or None)
		rows = cur.fetchall()
		cur.close()
		return rows

	def fetchone(self, query, *values):
		cur = self.new_cursor()
		cur.execute(query, vars = values or None)
		row = cur.fetchone()
		cur.close()
		return row

	def execute(self, query, *values):
		cur = self.new_cursor()
		cur.execute(query, vars = values or None)
		count = cur.rowcount
		cur.close()
		self.conn.commit()
		return count

	def stop(self):
		self.conn.close()



if __name__ == "__main__":
	db = Psql()
	query = "SELECT * FROM account"
	res = db.fetchall(query)
	print(res)



