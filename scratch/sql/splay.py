#!

# experimenting with MySQL
# this only works with python2 because mysql-python won't build under 3
# (but there are other DB drivers that will talk to MySQL which I haven't tried)

from sqlalchemy import *
import IPython


import csv
import io

def table2csv(conn, tbl, HEADER=True):
	# conn is a sqlalchemy connection object ( this *could* make a new connection per ,call, but that sounds like a recipe for lag)
	# tbl is a sqlalchemy.Table object
	# BUG: unicode support is busted in python's csv module, hence it is busted here too
	
	with io.BytesIO() as buffer: #"bytes" is python3 for "str"
		output = csv.writer(buffer)
		
		if HEADER:
			# SQLAlchemy's ImmutableColumnCollection is a fancy ordered dictionary of metadata
			# *ordered* is key here: it guantees that this next line is correct
			output.writerow(tbl.columns.keys())
			
		output.writerows(conn.execute(select([tbl]))) #<-- this line hides a huge amount of computation
		
		return buffer.getvalue()

if __name__ == '__main__':
	# There
	db = create_engine("mysql+mysqldb://root@127.0.0.1:3306/cmombour_sluceiidb") #mysqldb supports specifying a unix socket, but sqlalchemy doesn't seem to expose that. Maybe I just missed it.
	schema = MetaData() #XXX is this a misnomer?
	
	print("These tables available:", schema.tables.keys())

	conn = db.connect() #??? is this necessary? it seems to do things without it..
	schema.reflect(conn) #??
	
	analysisresults = schema.tables['analysisresults']
	print("The interesting table has these columns:",analysisresults.columns.keys())
	z = select([analysisresults.c.mean_budget, analysisresults.c.mean_util])
	print(z)
	r = conn.execute(z)
	csv = (table2csv(conn, analysisresults))
	print(csv)
	print("table2csv output a",type(csv))
	IPython.embed()