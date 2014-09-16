#!/usr/bin/env python

import time, sys, getopt, MySQLdb, string, math


class Mediator():
	def __init__(self,argument):
		print("\n")
		self.actor = Actor()
	def listTables(self):
		self.tables = self.actor.listTables()#returns an array of tuples
		self.table_list = list()
		if self.tables == 0:
			print("You do not currently have any tables listed here.\n Make yourself some tables using arg 'c' when running the program\n")
			exit()
		else:
			print("Which database are you connecting to? Your choices are:")
		for (x,table) in enumerate(self.tables):
			self.table_list.extend(table)#since you're looping you can turn this into array instead of tuples. like this syntax than the any() func
			print("\t --"+str(table[0]))#print each table
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
		elif argument == "c":
			self.actor.createTimer()
		else:
			return 0
	def tableAction(self):
		self.execution(self.my_table)

class Actor():
	def __init__(self):
		execfile('pass.py')
		self.db = MySQLdb.connect(host=self.host,user=self.user,passwd=self.pw,db=self.db)
		self.cur = self.db.cursor()
	def tryQuery(self,sql):
		try:
			self.cur.execute(sql)
			self.db.commit()
		except MySQLdb.Error as e:
			print "Error %d: %s" % (e.args[0],e.args[1])
			exit()
		finally:
			return self.cur
	def listTables(self):
		sql_tables = "SHOW TABLES;"
		self.tryQuery(sql_tables)
		all_tables = self.cur.fetchall()
		if len(all_tables)==0:
			return 0
		else:
			return all_tables
	def stopTimer(self,table):
		sql_verify_stop = "SELECT start,end,id FROM %s order by id DESC LIMIT 1" % table
		self.tryQuery(sql_verify_stop)
		result = self.cur.fetchone()
		if result[1] is not None:
			print "\n\n\nthis is not going to work. there is something here already\n\n\n"
			exit()
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
			self.cur.close()
			self.db.close()
			print "that went through\nbyebye"
	def goTimer(self,table):
		sql_verify_insert = "SELECT count(end), end FROM %(table)s order by id desc limit 1;" % {'table':table}
		self.tryQuery(sql_verify_insert)
		result = self.cur.fetchone()
		if result[0] is 0:
			if result[1] is None:
				print "\n\n\nyou didn't end the timer you fuckhead\n\n\n"
	 			exit()
 		else:#calculate all this time
 			start = time.time()
			start=math.floor(start)
			start = int(start)
			print start
			sql_insert = "INSERT INTO %(table)s (id,start) VALUES(DEFAULT, %(start_time)s);" % {'table':table,'start_time':start}
 			self.tryQuery(sql_insert)
 			print "don't forget to end!"
 			self.cur.close()
 			self.db.close()
 			exit()
	def createTimer(self):
		print "what table would you like to create?\n"
		table = raw_input()
		sql_create = "CREATE TABLE IF NOT EXISTS %(table)s (id MEDIUMINT NOT NULL AUTO_INCREMENT, day date, notes VARCHAR(300),start int(11), end int(11), duration VARCHAR(30), PRIMARY KEY(id));" % {'table':table}
		self.tryQuery(sql_create)
		self.cur.close()
		self.db.close()
		print "created %s sweet hot goodbye" % table
		exit()


##################
if len(sys.argv) < 2:
	print "yo you forgot an argument. use g to start timer, s to stop timer, and c to create a new table/client\n"
	exit()
else:
	argument = sys.argv[1]
med = Mediator(argument)
if med.isArg(argument)==0:
	print("not a proper argument. use g to start timer, s to stop timer, and c to create a new table/client")
else:
	med.listTables()

med.tableAction()