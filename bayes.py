import MySQLdb
import numpy as np
import time

def get_airports(): 
	airports = []
	numOfAirports = 0
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT IATA_CODE FROM airports')
	data_stmt = ()
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()
	numOfAirports = len(sample)
	for i in range(numOfAirports): 
		airports.append(str(sample[i][0]))
	return airports, numOfAirports

def airport_delay(airports, numOfAirports): 
	t1 = time.time()
	airportDelay = np.zeros((numOfAirports, 32))
	p_airportDelay = np.zeros((numOfAirports, 32))
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT  ORIGIN_AIRPORT, DEPARTURE_DELAY FROM flights WHERE ID > %s')
	data_stmt = ('1')
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()
	num = len(sample)
	print(int(sample[1][1]))
	for i in range(num): 
		airport = str(sample[i][0])
		if airport in airports: 
			index = airports.index(airport)
			delay = int(sample[i][1])
			if delay <= 0: 
				airportDelay[index][0] += 1
			elif delay > 300: 
				airportDelay[index][31] += 1
			else: 
				mag = delay // 10 + 1
				airportDelay[index][mag] += 1
	prefix = np.sum(airportDelay, axis = 1)
	for i in range(numOfAirports): 
		if prefix[i] != 0: 
			for j in range(32): 
				p_airportDelay[i][j] = round(airportDelay[i][j] / prefix[i], 4)
	t2 = time.time()
	
	return airportDelay, p_airportDelay, t2-t1

def get_carriers(): 
	carriers = []
	numOfCarriers = 0
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT IATA_CODE FROM airlines')
	data_stmt = ()
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()
	numOfCarriers = len(sample)
	for i in range(numOfCarriers): 
		carriers.append(str(sample[i][0]))
	return carriers, numOfCarriers

def carrier_delay(carriers, numOfCarriers): 
	t3 = time.time()
	carrierDelay = np.zeros((numOfCarriers, 32))
	p_carrierDelay = np.zeros((numOfCarriers, 32))
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT  AIRLINE, DEPARTURE_DELAY FROM flights WHERE ID > %s')
	data_stmt = ('1')
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()
	num = len(sample)
	for i in range(num): 
		carrier = str(sample[i][0])
		if carrier in carriers: 
			index = carriers.index(carrier)
			delay = int(sample[i][1])
			if delay <= 0: 
				carrierDelay[index][0] += 1
			elif delay > 300: 
				carrierDelay[index][31] += 1
			else: 
				mag = delay // 10 + 1
				carrierDelay[index][mag] += 1
	prefix = np.sum(carrierDelay, axis = 1)
	for i in range(numOfCarriers): 
		if prefix[i] != 0: 
			for j in range(32): 
				p_carrierDelay[i][j] = round(carrierDelay[i][j] / prefix[i], 4)
	t4 = time.time()
	return carrierDelay, p_carrierDelay, t4-t3

def period_delay(): 
	t3 = time.time()
	periodDelay = np.zeros((24, 32))
	p_periodDelay = np.zeros((24, 32))
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT  SCHEDULED_DEPARTURE, DEPARTURE_DELAY FROM flights WHERE ID > %s')
	data_stmt = ('1')
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	db.close()
	num = len(sample)
	for i in range(num): 
		dep = int(sample[i][0]) // 100
		if dep >= 0 and dep < 24: 
			delay = int(sample[i][1])
			if delay <= 0: 
				periodDelay[dep][0] += 1
			elif delay > 300: 
				periodDelay[dep][31] += 1
			else: 
				mag = delay // 10 + 1
				periodDelay[dep][mag] += 1
	prefix = np.sum(periodDelay, axis = 1)
	for i in range(24): 
		if prefix[i] != 0: 
			for j in range(32): 
				p_periodDelay[i][j] = round(periodDelay[i][j] / prefix[i], 4)
	t4 = time.time()
	return periodDelay, p_periodDelay, t4-t3

def inference(test_airport, test_carrier, test_time, airports, carriers, p_airportDelay, p_carrierDelay, p_periodDelay): 
	if test_airport in airports: 
		airport_index = airports.index(test_airport)
	else: 
		return 'failed'
	if test_carrier in carriers: 
		carrier_index = carriers.index(test_carrier)
	else: 
		return 'failed'
	period_index = test_time // 100
	estimate_airport = p_airportDelay[airport_index]
	estimate_carrier = p_carrierDelay[carrier_index]
	estimate_period = p_periodDelay[period_index]
	estimate = np.zeros((32))
	for i in range(32): 
		estimate[i] += estimate_airport[i]
		estimate[i] += estimate_carrier[i]
		estimate[i] += estimate_period[i]
	prefix = np.sum(estimate)
	for i in range(32): 
		estimate[i] = round(estimate[i] / prefix, 4)
	return estimate

def get_date(): 
	t1 = time.time()
	date = []
	numOfDates = 0
	for i in range(1, 13, 1): 
		for j in range(1, 32, 1): 
			date.append(int(100*i+j))
			numOfDates += 1
	t2 = time.time()
	return date, numOfDates, t2-t1

def date_delay(date, numOfDates): 
	t1 = time.time()
	dateDelay = np.zeros((numOfDates, 32))
	p_dateDelay = np.zeros((numOfDates, 32))
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	select_stmt = ('SELECT MONTH, DAY, DEPARTURE_DELAY FROM flights WHERE ID > %s')
	data_stmt = ('1')
	cursor.execute(select_stmt, data_stmt)
	sample = cursor.fetchall()
	num = len(sample)
	for i in range(num): 
		date0 = int(int(sample[i][0])*100 + int(sample[i][1]))
		if date0 in date: 
			index = date.index(date0)
			delay = int(sample[i][2])
			if delay <= 0: 
				dateDelay[index][0] += 1
			elif delay > 300: 
				dateDelay[index][31] += 1
			else: 
				mag = delay // 10 + 1
				dateDelay[index][mag] += 1
	prefix = np.sum(dateDelay, axis = 1)
	for i in range(numOfDates):
		if prefix[i] != 0:  
			for j in range(32): 
				p_dateDelay[i][j] = round(dateDelay[i][j] / prefix[i], 4)
	t2 = time.time()
	return dateDelay, p_dateDelay, t2-t1	


def insert_creat(date, numOfDates, p_dateDelay): 
	t1 = time.time()
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	for i in range(numOfDates): 
		row = []
		row.append(str(date[i]))
		for j in range(32): 
			row.append(str(round(100*p_dateDelay[i][j], 2)))
		insert_stmt = ('INSERT INTO prob_date (DAY, p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31)' 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
		data_stmt = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32])
		cursor.execute(insert_stmt, data_stmt)
		db.commit()
	db.close()
	t2 = time.time()
	return t2-t1


'''
def insert_creat(airports, numOfAirports, p_airportDelay): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	for i in range(numOfAirports): 
		row = []
		row.append(str(airports[i]))
		for j in range(32): 
			row.append(str(round(100*p_airportDelay[i][j], 2)))
		insert_stmt = ('INSERT INTO prob_airport (AIRPORT, p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31)' 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
		data_stmt = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32])
		cursor.execute(insert_stmt, data_stmt)
		db.commit()
	db.close()
	return
'''
'''
def insert_creat(carriers, numOfCarriers, p_carrierDelay): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	for i in range(numOfCarriers): 
		row = []
		row.append(str(carriers[i]))
		for j in range(32): 
			row.append(str(round(100*p_carrierDelay[i][j], 2)))
		insert_stmt = ('INSERT INTO prob_carrier (CARRIER, p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31)' 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
		data_stmt = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32])
		cursor.execute(insert_stmt, data_stmt)
		db.commit()
	db.close()
	return
'''
'''
def insert_hour(p_periodDelay): 
	db = MySQLdb.connect(user='root',db='initialDemo',passwd='',host='localhost')
	cursor = db.cursor()
	for i in range(24): 
		row = []
		row.append(str(i))
		for j in range(32): 
			row.append(str(round(100*p_periodDelay[i][j], 2)))
		insert_stmt = ('INSERT INTO prob_period (HOUR, p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31)' 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
		data_stmt = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32])
		cursor.execute(insert_stmt, data_stmt)
		db.commit()
	db.close()
	return
'''



#airports, numOfAirports = get_airports()
#airportDelay, p_airportDelay, runtime1 = airport_delay(airports, numOfAirports)
#carriers, numOfCarriers = get_carriers()
#carrierDelay, p_carrierDelay, runtime2 = carrier_delay(carriers, numOfCarriers)
#periodDelay, p_periodDelay, runtime3 = period_delay()
date, numOfDates, rt1 = get_date()
dateDelay, p_dateDelay, rt2 = date_delay(date, numOfDates)
rt3 = insert_creat(date, numOfDates, p_dateDelay)

#estimate = inference('ORD', 'UA', 1437, airports, carriers, p_airportDelay, p_carrierDelay, p_periodDelay)
#insert_creat(carriers, numOfCarriers, p_carrierDelay)
#insert_hour(p_periodDelay)

print(rt1)
print(rt2)
print(rt3)
print(numOfDates)
print(p_dateDelay[3][0])
#print(numOfCarriers)
#print(estimate)

