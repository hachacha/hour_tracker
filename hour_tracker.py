#!/usr/bin/env python

import time, sys, getopt, MySQLdb, string, math

#would like to make this into a postgres app so i can do some parametized strings
class Mediator():
	def __init__(self,argument):
		print("\n")
		self.actor = Actor()
	def listTables(self):
		self.tables = self.actor.listTables()#returns an array of tuples
		self.table_list = list()#is just a list.
		if self.tables == 0:
			print("You do not currently have any tables listed here.\n Make yourself some tables using arg 'c' when running the program\n")
			exit()
		else:
			print("Which database are you connecting to? Your choices are:")
		for x in self.tables:
			self.table_list.extend(x)#since you're looping you can turn this into array instead of tuples. like this syntax more than the any() func
			print("\t --"+str(x[0]))#print each table
		choice = raw_input()
		if choice in self.table_list:
			self.my_table = str(choice)
		else:
			print("That's not an existing database.\n\n")
			exit()
	def isArg(self,argument):
		if argument == "g":
			self.execution = self.actor.goTimer
			return 1
		elif argument == "s":
			self.execution = self.actor.stopTimer
			return 1
		elif argument == "n":
			self.execution = self.actor.addNotes
			return 1
		elif argument == "c":
			print "what table would you like to create?\n"
			table = raw_input()
			self.actor.createTimer(table)
		else:
			return 0
	def tableAction(self):
		print self.execution(self.my_table)
		exit()

class Actor():
	def __init__(self):
		execfile('pass.py')
		self.db = MySQLdb.connect(host=self.host,user=self.user,passwd=self.pw,db=self.db)
		self.cur = self.db.cursor()
	def closeOut(self):
		self.cur.close()
		self.db.close()
	def tryQuery(self,sql):
		try:
			self.cur.execute(sql)
			self.db.commit()
		except MySQLdb.Error as e:
			print e.args
			return "Error %d: %s" % (e.args[0],e.args[1])
		finally:
			return self.cur
	def tryInt(self,u_input):
		try:
		    u_input = int(u_input)
		except ValueError:
		    return False
		else:
			return True
	def listTables(self):
		sql_tables = "SHOW TABLES;"
		self.tryQuery(sql_tables)
		all_tables = self.cur.fetchall()
		if len(all_tables)==0:
			return 0
		else:
			return all_tables
	def stopTimer(self,table):
		sql_verify_stop = "SELECT start,end,id FROM %(table)s order by id DESC LIMIT 1" % {'table':table}
		self.tryQuery(sql_verify_stop)
		result = self.cur.fetchone()
		if result[1] is not None:
			return "\n\n\nthis is not going to work. there is something here already\n\n\n"
		else:
			start= int(result[0])
			theID = int(result[2])
			end = time.time()
			end = math.floor(end)
			end = int(end)
			duration = end - start
			duration = time.strftime("%H:%M:%S",time.gmtime(duration))
			today = time.strftime("%Y-%m-%d",time.gmtime(time.time()))
			sql_stop = "UPDATE %(table)s SET end=%(end)s, duration='%(duration)s', day = '%(today)s' WHERE id=%(id)s;"%{"table":table,"end":end,"duration":duration,"today":today,"id":theID}
			self.tryQuery(sql_stop)
			self.closeOut()
			return "that went through\ntotal time: "+duration+"\nbyebye"

	def goTimer(self,table):
		sql_verify_insert = "SELECT count(end), end FROM %(table)s order by id desc limit 1;" % {'table':table}
		self.tryQuery(sql_verify_insert)
		result = self.cur.fetchone()
		if result[0] is 0:
			if result[1] is None:
				return "\n\n\nyou didn't end the timer you fuckhead\n\n\n"
 		else:#calculate all this time
 			start = time.time()
			start=math.floor(start)
			start = int(start)
			sql_insert = "INSERT INTO %(table)s (id,start) VALUES(DEFAULT, %(start_time)s);" % {'table':table,'start_time':start}
 			self.tryQuery(sql_insert)
 			self.closeOut()
 			return "don't forget to end!"

 	def addNotes(self,table):
 		print "how many entries back are you trying to look? Please enter an integer\n"
 		limit = raw_input()
 		if self.tryInt(limit) == False:
 			return "that was not an int you are dumb."
 		limit = int(limit)
 		sql_show_rows = "SELECT id, FROM_UNIXTIME(start) FROM %(table)s order by id desc limit %(limit)d;" % {'table':table,'limit':limit}
 		self.tryQuery(sql_show_rows)
 		result = self.cur.fetchall()
 		print "\n\n please choose an ID to add a note to(must be integer):\n"
 		for i in result:
 			print "\tID: "+str(i[0]) + "  from date(starttime): " + str(i[1])
 		n_id = raw_input()
 		if self.tryInt(n_id)==False:
 			return "that was not an int you are dumb."
 		n_id = int(n_id)
 		print "enter your notes below (mysqldb does not include parametized strings so escape all double quotes plz sry):\n"
 		u_notes = raw_input()
 		print u_notes
 		sql_note_query = "UPDATE %(table)s SET notes = \"%(notes)s\"" WHERE id = %(n_id)d;" % {'table':table,'notes':str(u_notes),'n_id':n_id} 
 		self.tryQuery(sql_note_query)
 		self.closeOut()
 		return "nice notes. i am sure your employer is going absolutely gaga"
 		
 			
	def createTimer(self,table):
		sql_create = "CREATE TABLE IF NOT EXISTS %(table)s (id MEDIUMINT NOT NULL AUTO_INCREMENT, day date, notes VARCHAR(300),start int(11), end int(11), duration VARCHAR(30), PRIMARY KEY(id));" % {'table':table}
		self.tryQuery(sql_create)
		self.closeOut()
		print "created %s sweet hot goodbye" % table
		exit()


##############################
if len(sys.argv) < 2:
	print "yo you forgot an argument. use g to start timer, s to stop timer, n to add notes to recent entry, and c to create a new table/client\n"
	exit()
else:
	argument = sys.argv[1]
med = Mediator(argument)
if med.isArg(argument)==0:
	print("not a proper argument. use g to start timer, s to stop timer, n to add notes to a recent entry, and c to create a new table/client\n")
else:
	med.listTables()

med.tableAction()
