import json

import mysql.connector,sys
import datetime
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template
from random import randint

app = Flask(__name__)

@app.route('/')
def renderLoginPage():
    return render_template('login.html')


@app.route('/login' , methods = ['POST'])
def verifyAndRenderRespective():
	username = request.form['username']
	password = request.form['password']
	res = runQuery("SELECT id_client, password FROM Clients")
	credentials = {}
	for client in res:
		credentials[client[0]] = client[1]
	try:
		if username == 'manager' and password == 'manager':
			res = runQuery('call delete_old()')
			return render_template('manager.html')
		elif credentials[username] == password:
			res = runQuery('call delete_old()')
			return render_template('user.html', data = [username])
		else:
			return render_template('loginfail.html')
	except Exception as e:
		print(e)
		return render_template('loginfail.html')


# Routes for user
@app.route('/getTrainsDate', methods = ['POST'])
def trainsOnDate():
	date = request.form['date']

	#res = runQuery("call find_billets('" + date + "')")
	res = runQuery("select distinct date(depart), gare_depart, gare_arrive from Billets natural join Trajets where date(depart)='"+date+"'")
	print(res)
	if res == []:
		return '<h4>No Train Today</h4>'
	else:
		print(res[0])
		return render_template('billets.html', trains = res)


@app.route('/getTimings', methods = ['POST'])
def timingsForTrain():
	date = request.form['date']
	gare_depart = request.form['gare_depart']
	gare_arrivee = request.form['gare_arrivee']

	res = runQuery("select time(depart), id_trajet, id_billet from Billets natural join Trajets where date(depart)='"+ date + "' and Trajets.gare_depart = '"+ gare_depart + "'  and gare_arrive = '"+ gare_arrivee + "'")
	return render_template('timings.html',timings = res)


@app.route('/getBilletID', methods = ['POST'])
def getBilletID():
	id_billet = request.form['id_billet']
	res = runQuery("select id_billet from Voitures group by id_billet having sum(nb_place) >0 and id_billet = '"+id_billet+"'")
	return jsonify({'available_voiture':res[0][0]})


@app.route('/getAvailableSeats', methods = ['POST'])
def getSeating():
	id_billet = request.form['available_voiture']
	totalFenetre = runQuery("SELECT count(*) FROM Seats WHERE id_billet = '"+ id_billet +"' and fenetre_couloir = 'f' and available = 1")[0]
	totalCouloir = runQuery("SELECT count(*) FROM Seats WHERE id_billet = '"+ id_billet +"' and fenetre_couloir = 'c' and available = 1")[0]

	return render_template('seating.html', totalFenetre = totalFenetre, totalCouloir = totalCouloir)


@app.route('/getPrice', methods = ['POST'])
def getPriceForClass():
	id_billet = request.form['billet']
	seatType = request.form['seatType']
	username = request.form['username']

	res = runQuery("select prix from Billets where id_billet = '"+ id_billet +"'")
	price = int(res[0][0])

	res = runQuery("select percent from Clients natural join Reductions where id_client = '"+ username +"'")
	reduction = float(res[0][0])

	price = price*reduction

	return '<h5>Ticket Price: € '+str(price)+'</h5>\
	<h5>Click Reset Button to Cancel the reservation</h5>\
	<button onclick="confirmBooking()">Confirm</button>'


@app.route('/insertBooking', methods = ['POST'])
def createBooking():
	id_billet = request.form['id_billet']
	username = request.form['username']
	seatType = request.form['seatType']

	ticketNo = str(randint(0, 214748))
	res = runQuery("select num_seat, num_voiture from Seats where fenetre_couloir='"+seatType+"' and id_billet = '"+id_billet+"' order by rand() limit 1")

	num_seat = res[0][0]
	num_voiture = res[0][1]
	res = runQuery("INSERT INTO Booked_tickets VALUES (%s,%s,%s,%s,%s)", params = (ticketNo, username, id_billet, num_seat, num_voiture))

	if res == []:
		return '<h5>Ticket Successfully Booked</h5>\
		<h6>Ticket Number: '+str(ticketNo)+'</h6>'


# Routes for manager
@app.route('/getTrainOnDate', methods = ['POST'])
def getTrainsOnThisDate():
	date = request.form['date']

	res = runQuery("select id_booked, id_client, num_seat, num_voiture, id_billet, depart, gare_depart, gare_arrive from Booked_tickets natural join Billets natural join Trajets WHERE date(depart) = '"+date+"'")

	if res == []:
		return '<h4>No Bookings Today</h4>'
	else:
		return render_template('bookedtickets.html', tickets = res)


@app.route('/getBookedWithBilletID', methods = ['POST'])
def getBookedTickets():
	id_billet = request.form['id_billet']

	res = runQuery("select id_billet, id_train, depart, prix, gare_depart, gare_arrive, ville_depart, temps from Billets natural join Trajets where id_billet = '"+id_billet+"'")

	return render_template('infodetaillee.html', info=res)


@app.route('/fetchBilletInsertForm', methods = ['GET'])
def getBilletDetail():
	return render_template('billetdetails.html')


@app.route('/insertBilletInfo', methods = ['POST'])
def insertBillet():
	id_billet = request.form['id_billet']
	id_train = request.form['id_train']
	prix = request.form['prix']
	g_depart = request.form['g_depart']
	g_arrivee = request.form['g_arrivee']
	h_depart = request.form['h_depart']
	j_depart = request.form['j_depart']

	# find the id of the trajet
	res = runQuery("select id_trajet from Trajets where gare_depart='"+g_depart+"' and gare_arrive='"+g_arrivee+"'")
	id_trajet = res[0][0]

	# put date and time of the departure into good format
	j_h_depart = j_depart + ' ' +h_depart
	# insert into tables
	res = runQuery("insert into Billets values (%s,%s,%s,%s,%s)", (id_billet, id_train, id_trajet, j_h_depart, prix))
	return '<h5>Successful !</h5>'

def runQuery(query, params=None):
	try:
		db = mysql.connector.connect(
			host='localhost',
			database='my_sncf_reservation',
			user='root',
			password='rootpassword')

		if db.is_connected():
			print("Connected to MySQL, running query: ", query)
			cursor = db.cursor(buffered = True)
			cursor.execute(query, params)
			db.commit()
			res = None
			try:
				res = cursor.fetchall()
			except Exception as e:
				print("Query returned nothing, ", e)
				return []
			return res

	except Exception as e:
		print(e)
		return e

	finally:
		db.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
 
