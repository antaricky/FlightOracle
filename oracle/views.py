# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.template import Context, loader
from django.shortcuts import render_to_response
import MySQLdb
from django.http import HttpResponse
from django.db   import connections
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import random
import numpy as np
import urllib


def index(request):
	return render_to_response('index1.html')



def find(request):
	Carrier = request.GET.get('Carrier','XX')
	Departure = request.GET.get('Departure','IAD')  
	Arrival = request.GET.get('Arrival','TPA')
	Date = request.GET.get('Date','2005-01-01')

	Year = Date[0:4]
	Month = str(int(Date[5:7]))
	Day = str(int(Date[8:10]))
	record = getrecord(Carrier,Departure,Arrival,Year,Month,Day)
	if len(record) == 0:
		#return HttpResponse("No flights found")
		return render(request, "index.htm", {"result": 'No Flights Found'})
	else:
		return render(request, "index.htm", {"result": record})
	'''
		#result = str(record.lastname) + ', ' + str(record.firstname)
	return HttpResponse(record.firstname)
	'''

def getrecord(Carrier,Departure,Arrival,Year,Month,Day):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	#db = MySQLdb.connect(user='root',db='flightdb',passwd='',host='localhost')
	cursor = db.cursor()
	if Carrier == 'XX':
		select_stmt = ('SELECT * FROM flights WHERE YEAR = %s and MONTH = %s and DAY = %s and ORIGIN_AIRPORT = %s and DESTINATION_AIRPORT = %s')
		data_stmt = (Year, Month, Day, Departure, Arrival)
	else: 
		select_stmt = ('SELECT * FROM flights WHERE YEAR = %s and MONTH = %s and DAY = %s and AIRLINE = %s and ORIGIN_AIRPORT = %s and DESTINATION_AIRPORT = %s')
		data_stmt = (Year, Month, Day, Carrier, Departure, Arrival)

	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()

    	return sample



def insert(request):
	Carrier = request.GET.get('Carrier','XX')
	Departure = request.GET.get('Departure','IAD')  
	Arrival = request.GET.get('Arrival','TPA')
	Date = request.GET.get('Date','2005-01-01')
	ArrivalDelay = request.GET.get('ArrivalDelay','0')
	FlightNumber = request.GET.get('FlightNumber', '0')
	
	Year = Date[0:4]
	Month = str(int(Date[5:7]))
	Day = str(int(Date[8:10]))
	res = insertRecords(Carrier, Departure, Arrival, Year, Month, Day, ArrivalDelay, FlightNumber)
	if res == 'succeeded':
		return render(request, "index.htm", {"insertResult": 'You have successfully inserted a record !'})
	else:
		return render(request, "index.htm", {"insertResult": 'Record already exists!'})

def insertRecords(Carrier, Departure, Arrival, Year, Month, Day, ArrivalDelay, FlightNumber):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	#check if exsisted
	select_stmt = ('SELECT * FROM flights WHERE YEAR = %s AND MONTH = %s AND DAY = %s AND AIRLINE = %s AND ORIGIN_AIRPORT = %s AND DESTINATION_AIRPORT = %s AND FLIGHT_NUMBER = %s')
	select_data = (Year, Month, Day, Carrier, Departure, Arrival, FlightNumber)
	cursor.execute(select_stmt, select_data)
	exist = cursor.fetchall()
	if len(exist) != 0:
		db.close()
		return 'existed'
	else: 
		insert_stmt = (	"INSERT INTO flights (YEAR,MONTH,DAY,AIRLINE,ORIGIN_AIRPORT,DESTINATION_AIRPORT,ARRIVAL_DELAY,FLIGHT_NUMBER)"
						"VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
						)
		#insert_stmt = ('INSERT INTO flights SET YEAR = %s AND MONTH = %s AND DAY = %s AND AIRLINE = %s AND ORIGIN_AIRPORT = %s AND DESTINATION_AIRPORT = %s AND ARRIVAL_DELAY = %s AND FLIGHT_NUMBER = %s')
		data_stmt = (Year, Month, Day, Carrier, Departure, Arrival, ArrivalDelay, FlightNumber)
		cursor.execute(insert_stmt, data_stmt)
		select_stmt = ('SELECT ID FROM flights WHERE YEAR = %s AND MONTH = %s AND DAY = %s AND AIRLINE = %s AND FLIGHT_NUMBER = %s AND ORIGIN_AIRPORT = %s AND DESTINATION_AIRPORT = %s')
		data_stmt = (Year, Month, Day, Carrier, FlightNumber, Departure, Arrival)
		cursor.execute(select_stmt, data_stmt)
		sample = cursor.fetchone()
		insert_stmt = ('INSERT INTO miniflights(YEAR, MONTH, DAY, AIRLINE, FLIGHT_NUMBER, ID)' 'VALUES(%s, %s, %s, %s, %s, %s)')
		data_stmt = (Year, Month, Day, Carrier, FlightNumber, str(sample[0]))
		cursor.execute(insert_stmt, data_stmt)
		db.commit()
		db.close()
		return 'succeeded'



def delete(request):
	ID = request.GET.get('ID', '0')
	res = deleteRecords(ID)
	if res != 'does not exist':
		return render(request, "index.htm", {"deleteResult": 'You have successfully deleted a record !'})
	else:
		return render(request, "index.htm", {"deleteResult": 'Record does not exist!'})

def deleteRecords(ID):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	cursor.execute('SELECT * FROM flights WHERE ID = %s', ID)
	exist = cursor.fetchall()
	if len(exist) != 0:
		# delete_stmt = ('DELETE FROM flights WHERE ID = %s')
		# data_stmt = (ID)
		# cursor.execute(delete_stmt, data_stmt)
		cursor.execute('SET @FID = %s', str(exist[0][0]))
		cursor.execute('CALL delete_record(@FID)', ())
		db.commit()
		db.close()
		return 'succeeded'
	else: 
		db.close()
		return 'does not exist'


def update(request):
	Carrier = request.GET.get('Carrier','XX')
	Departure = request.GET.get('Departure','IAD')  
	Arrival = request.GET.get('Arrival','TPA')
	Date = request.GET.get('Date','2015-01-01')
	ArrivalDelay = request.GET.get('ArrivalDelay','0')
	FlightNumber = request.GET.get('FlightNumber', '0')
	ArrivalDelay = request.GET.get('ArrivalDelay','0')
	Year = Date[0:4]
	Month = str(int(Date[5:7]))
	Day = str(int(Date[8:10]))
	res = updateRecords(Carrier, Departure, Arrival, FlightNumber, Year, Month, Day, ArrivalDelay)
	if res == 'succeeded':
		return render(request, "index.htm", {"updateResult": 'You have successfully updated a record !'})
	else: 
		return render(request, "index.htm", {"updateResult": 'Record does not exist!'})

def updateRecords(Carrier, Departure, Arrival, FlightNumber, Year, Month, Day, ArrivalDelay):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT * FROM flights WHERE YEAR = %s AND MONTH = %s AND DAY = %s AND AIRLINE = %s AND ORIGIN_AIRPORT = %s AND DESTINATION_AIRPORT = %s AND FLIGHT_NUMBER = %s')
	select_data = (Year, Month, Day, Carrier, Departure, Arrival, FlightNumber)
	cursor.execute(select_stmt, select_data)
	exist = cursor.fetchall()
	if len(exist) != 0:
		update_stmt = ('UPDATE flights SET ARRIVAL_DELAY = %s WHERE YEAR = %s AND MONTH = %s AND DAY = %s AND AIRLINE = %s AND ORIGIN_AIRPORT = %s AND DESTINATION_AIRPORT = %s AND FLIGHT_NUMBER = %s')
		data_stmt = (ArrivalDelay, Year, Month, Day, Carrier, Departure, Arrival, FlightNumber)	
		cursor.execute(update_stmt, data_stmt)
		db.commit()
		db.close()

		return 'succeeded'
	else: 
		db.close()
		return 'does not exist'


def viewstat(request): 
	ID = request.GET.get('ID')
	result = findStat(ID)
	return render(request, "index.htm", {"viewResult": result})

def findStat(ID): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT FS.AVG_DEPARTURE_DELAY, FS.AVG_ARRIVAL_DELAY FROM flights F, FlightStat FS WHERE F.ID = %s AND FS.AIRLINE = F.AIRLINE AND FS.FLIGHT_NUMBER = F.FLIGHT_NUMBER')
	data_stmt = (ID)
	cursor.execute(select_stmt, data_stmt)
	res = cursor.fetchall()
	db.close()
	return res

def login(request):
	Email		= request.GET.get('Email')
	Password	= request.GET.get('Password')
	sample 		= userLogin(Email,Password)
	if len(sample) == 0:
		return render(request, "index1.html", {"loginResult": 'Incorrect Email or Password'})
	else: 
		FirstName = sample[0][0];
		LastName = sample[0][1];

		response = 'Welcome back, '
		response += FirstName
		response += '!'
		res = render(request, "maps.html", {"loginResult": response})
		res.set_cookie('UserID', sample[0][4])
		return res

def register(request):
	FirstName 	= request.GET.get('FirstName')
	LastName 	= request.GET.get('LastName')
	Email		= request.GET.get('Email')
	Password	= request.GET.get('Password')
	status 		= userRegiser(FirstName,LastName,Email,Password)
	#return	HttpResponse(status)
	if status == 'User Already Exist': 
		return render(request, "index1.html", {"registerResult": 'User Already Exist! '})
	else: 
		response = 'Welcome, '
		response += FirstName
		response += '! '
		res = render(request, "maps.html", {"registerResult": response})
		res.set_cookie('UserID', status[0][0])
		return res
	

def userLogin(Email, Password):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT * FROM users WHERE Email = %s and Password = %s')
	data_stmt = (Email, Password)
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()
	return sample


def userRegiser(FirstName,LastName,Email,Password):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	#check if user already exist
	select_stmt = ('SELECT * FROM users WHERE Email = %s')
	data_stmt = (Email)
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	if len(sample) != 0:
		db.close()
		return 'User Already Exist'
	else:
		insert_stmt = ('INSERT INTO users (FirstName, LastName, Email, Password)' 'VALUES(%s, %s, %s, %s)')
		data_stmt = (FirstName, LastName, Email, Password)
		cursor.execute(insert_stmt, data_stmt)
		db.commit()
		select_stmt = ('SELECT UID FROM users WHERE Email = %s')
		data_stmt = (Email)
		cursor.execute(select_stmt, data_stmt)
		sample = cursor.fetchall()
		db.close()
		return sample
		
def chat(request):
	return render(request,"chat.html")
	
def maps(request): 
	return render(request, "maps.html")

def table(request): 
	if 'UserID' in request.COOKIES: 
		UID = request.COOKIES['UserID']
	sample = getFlight(UID)
	Data = []
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	for i in range(len(sample)): 
		record = []
		#string = str(sample[i][0])
		#string += '-'
		#if sample[i][1] < 10: 
		#	string += '0'
		string = months[sample[i][1]-1]
		string += '-'
		if sample[i][2] < 10: 
			string += '0'
		string += str(sample[i][2])
		record.append(string)
		record.append(sample[i][3])
		record.append(sample[i][4])
		#record.append(sample[i][5])
		#record.append(sample[i][6])
		h = int(sample[i][5] // 100)
		m = int(sample[i][5] % 100)
		if h < 10: 
			dept = '0'
			dept += str(h)
		else: 
			dept = str(h)
		dept += ' : '
		if m < 10: 
			dept += '0'
		dept += str(m)
		record.append(dept)
		h = int(sample[i][6] // 100)
		m = int(sample[i][6] % 100)
		if h < 10: 
			arvl = '0'
			arvl += str(h)
		else: 
			arvl = str(h)
		arvl += ' : '
		if m < 10: 
			arvl += '0'
		arvl += str(m)
		record.append(arvl)
		record.append(sample[i][7])
		record.append(sample[i][8])
		Data.append(record)
	return render(request, "table.html", {"result": Data})

def getFlight(UID): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT F.YEAR, F.MONTH, F.DAY, A1.AIRPORT, A2.AIRPORT, F.SCHEDULED_DEPARTURE, F.SCHEDULED_ARRIVAL, F.AIRLINE, F.FLIGHT_NUMBER FROM flights F, myflights M, airports A1, airports A2 WHERE M.UID = %s AND F.ID = M.FlightID AND A1.IATA_CODE = F.ORIGIN_AIRPORT AND A2.IATA_CODE = F.DESTINATION_AIRPORT')
	data_stmt = (UID)
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	return sample  

def user(request): 
	if 'UserID' in request.COOKIES: 
		UID = request.COOKIES['UserID']
	sample = getUser(UID)
	return render(request, "user.html", {"FirstName": sample[0][0], "LastName": sample[0][1]})


def getUser(UID): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	cursor.execute('SELECT FirstName, LastName FROM users WHERE UID = %s', UID)
	sample = cursor.fetchall()
	db.close()
	return sample

def updateProfile(request):
	if 'UserID' in request.COOKIES: 
		UID = request.COOKIES['UserID']
	FirstName 	= request.GET.get('FirstName')
	LastName 	= request.GET.get('LastName')
	#Email		= request.GET.get('Email')
	Password	= request.GET.get('Password')
	sample 		= userUpdate(UID, FirstName,LastName,Password)
	if sample == 'succeeded':
		return redirect("user")
	else:
		return render(request, "user.html", {"result":'Ooops...'})

def userUpdate(UID, FirstName,LastName,Password): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	update_stmt = ('UPDATE users SET FirstName = %s, LastName = %s, Password = %s WHERE UID = %s')
	data_stmt = (FirstName, LastName, Password, UID)
	cursor.execute(update_stmt, data_stmt)
	db.commit()
	db.close()
	return 'succeeded'

def addFlight(request): 
	if 'UserID' in request.COOKIES: 
		UID = request.COOKIES['UserID']
	Carrier = request.GET.get('Carrier')
	FlightNumber = request.GET.get('FlightNumber')
	Date = request.GET.get('Date')
	Month = str(int(Date[5:7]))
	Day = str(int(Date[8:10]))
	Year = str(int(Date[0:4]))
	status = userAddFlight(UID, Carrier, FlightNumber, Month, Day, Year)
	if status == 'failed': 
		return render(request, "maps.html", {"result":'Flight does not exist! '})
	elif status == 'added': 
		return render(request, "maps.html", {"result":'You have already added this flight! '})
	else: 
		return render(request, "maps.html", {"result": status})



def userAddFlight(UID, Carrier, FlightNumber, Month, Day, Year): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	#check whether the flight exists
	select_stmt = ('SELECT ID FROM miniflights WHERE AIRLINE = %s AND FLIGHT_NUMBER = %s AND MONTH = %s AND DAY = %s')
	data_stmt = (Carrier, FlightNumber, Month, Day)
	cursor.execute(select_stmt, data_stmt)
	# cursor.execute('SET @MONTH_I = %s', Month)
	# cursor.execute('SET @DAY_I = %s', Day)
	# cursor.execute('SET @AIRLINE_I = %s', Carrier)
	# cursor.execute('SET @FLIGHT_NUMBER_I = %s', FlightNumber)
	# cursor.execute('SET @FID_O = %s', '0')
	# cursor.execute('CALL select_fid(@MONTH_I, @DAY_I, @AIRLINE_I, @FLIGHT_NUMBER_I, @FID_O)', ())
	# cursor.execute('SELECT @FID_O', ())
	sample = cursor.fetchall()
	sp = str(sample)
	if len(sample) == 0 : 
		db.close()
		return 'failed'
	else :
		select_stmt = ('SELECT FlightID FROM myflights WHERE UID = %s AND FlightID = %s')
		data_stmt = (UID, sample[0])
		cursor.execute(select_stmt, data_stmt)
		sample0 = cursor.fetchall()
		if len(sample0) != 0:
			db.close() 
			return 'added'
		else: 
			#insert_stmt = ('INSERT INTO myflights (UID, FlightID)' 'VALUES(%s, %s)')
			#insert_data = (UID, sample)
			#cursor.execute(insert_stmt, insert_data)
			cursor.execute('SET @userid = %s', UID)
			cursor.execute('SET @flightid = %s', str(sample[0][0]))
			cursor.execute('CALL insert_myflight (@userid, @flightid)', ())
			#res = cursor.fetchall()
			db.commit()
			db.close()
			return 'succeeded'

def deleteFlight(request): 
	if 'UserID' in request.COOKIES: 
		UID = request.COOKIES['UserID']
	Carrier = request.GET.get('Carrier')
	FlightNumber = request.GET.get('FlightNumber')
	Date = request.GET.get('Date')
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	m = str(Date[0:3])
	for i in range(12): 
		if months[i] == m: 
			Month = str(i+1)
	Day = str(int(Date[4:6]))
	Year = str(2015)
	status = userDeleteFlight(UID, Carrier, FlightNumber, Month, Day, Year)
	return redirect("table")

def userDeleteFlight(UID, Carrier, FlightNumber, Month, Day, Year): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT ID FROM miniflights WHERE MONTH = %s AND DAY = %s AND AIRLINE = %s AND FLIGHT_NUMBER = %s')
	data_stmt = (Month, Day, Carrier, FlightNumber)
	cursor.execute(select_stmt, data_stmt)
	# cursor.execute('SET @MONTH_I = %s', Month)
	# cursor.execute('SET @DAY_I = %s', Day)
	# cursor.execute('SET @AIRLINE_I = %s', Carrier)
	# cursor.execute('SET @FLIGHT_NUMBER_I = %s', FlightNumber)
	# cursor.execute('SET @FID_O = %s', '0')
	# cursor.execute('CALL select_fid(@MONTH_I, @DAY_I, @AIRLINE_I, @FLIGHT_NUMBER_I, @FID_O)', ())
	# # cursor.execute('SELECT @FID_O', ())
	sample = cursor.fetchone()
	fid = str(sample)
	delete_stmt = ('DELETE FROM myflights WHERE UID = %s AND FlightID = %s')
	data_stmt = (UID, sample)
	cursor.execute(delete_stmt, data_stmt)
	db.commit()
	db.close()
	return

def deleteAccount(request):
	#FirstName 	= request.GET.get('FirstName')
	#LastName 	= request.GET.get('LastName')
	if 'UserID' in request.COOKIES: 
		UID = int(request.COOKIES['UserID'])
	Email		= request.GET.get('Email')
	Password	= request.GET.get('Password')
	sample 		= userDelete(UID, Email,Password)
	if sample == 'succeeded':
		return redirect("index")
	else:
		return redirect("user")
	

def userDelete(UID, Email, Password):
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT UID FROM users WHERE Email = %s and Password = %s')
	data_stmt = (Email, Password)
	cursor.execute(select_stmt, data_stmt)
	check = cursor.fetchall()
	if int(check[0][0]) == UID: 
		delete_stmt = ('DELETE FROM users WHERE UID = %s')
		data_stmt = (UID)
		cursor.execute(delete_stmt, data_stmt)
		db.commit()
		db.close()
		return 'succeeded'
	else: 
		db.close()
		return 'failed'

def logout(request): 
	response = HttpResponseRedirect('/oracle')
	response.delete_cookie('UserID')
	return response

def viewEstimate(request): 
	Date = request.GET.get('Date')
	FlightNumber = request.GET.get('FlightNumber')
	FlightNumber = str(FlightNumber)
	Scheduled = request.GET.get('Scheduled')
	Carrier = request.GET.get('Carrier')
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	Month = months.index(Date[0:3])+1
	Day = int(Date[4:6])
	date = str(100*Month+Day)
	hour = str(int(Scheduled[0:2]))
	p_date, p_carrier, p_hour, p_airport, airport = estimate(date, Carrier, hour, FlightNumber)
	p = np.zeros((32))
	for i in range(32): 
		p[i] += int(p_date[i+1]) + int(p_carrier[i+1]) + int(p_hour[i+1]) + int(p_airport[i+1])
	prefix = np.sum(p)
	for i in range(32): 
		p[i] = round(p[i] / prefix * 100, 2)
	p_simplified = []
	for i in range(10): 
		if i < 7: 
			p_simplified.append(str(p[i]))
		elif i == 7: 
			p_simplified.append(str(p[7]+p[8]+p[9]+p[10]+p[11]+p[12]))
		elif i == 8: 
			p_simplified.append(str(p[13]+p[14]+p[15]+p[16]+p[17]+p[18]))
		else: 
			p_simplified.append(str(p[19]+p[20]+p[21]+p[22]+p[23]+p[24]+p[25]+p[26]+p[27]+p[28]+p[29]+p[30]+p[31]))
	return render(request, "table.html", {"viewResult": p_simplified})
	#return p_simplified



def estimate(date, Carrier, hour, FlightNumber): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	month = str(int(date) // 100)
	day = str(int(date) % 100)
	select_stmt = ('SELECT ID FROM miniflights WHERE MONTH = %s AND DAY = %s AND AIRLINE = %s AND FLIGHT_NUMBER = %s')
	data_stmt = (month, day, Carrier, FlightNumber)
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchone()
	fid = str(int(sample[0]))
	select_stmt = ('SELECT ORIGIN_AIRPORT FROM flights WHERE ID = %s')
	data_stmt = (fid)
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchone()
	airport = str(sample[0])
	select_stmt = ('SELECT * FROM prob_date WHERE DAY = %s')
	data_stmt = (date)
	cursor.execute(select_stmt, data_stmt)
	p_date = cursor.fetchone()
	select_stmt = ('SELECT * FROM prob_carrier WHERE CARRIER = %s')
	data_stmt = (Carrier)
	cursor.execute(select_stmt, data_stmt)
	p_carrier = cursor.fetchone()
	select_stmt = ('SELECT * FROM prob_period WHERE HOUR = %s')
	data_stmt = (hour)
	cursor.execute(select_stmt, data_stmt)
	p_period = cursor.fetchone()
	select_stmt = ('SELECT * FROM prob_airport WHERE AIRPORT = %s')
	data_stmt = (airport)
	cursor.execute(select_stmt, data_stmt)
	p_airport = cursor.fetchone()
	db.close()
	return p_date, p_carrier, p_period, p_airport, airport