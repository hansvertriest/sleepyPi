import os
from flask import Flask
import socket
import fcntl
import struct
import firebase_admin
from firebase_admin import credentials, firestore
import threading

# firebase
cred = credentials.Certificate("./config.json")
firebase_admin.initialize_app(cred)

# connect firestore
db = firestore.client()


#  init flask
app = Flask(__name__)

# get ip adress
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def update_state(task_input, state_input):
	f= open("tasks.txt","r+")

	# modify tasks.txt
	lines = f.readlines()
	new_lines = []
	for line in lines:
		line = line.split('\t')
		task = line[0].replace('\x00', '')
		state = line[1].replace('\n', '')
		if (task == task_input):
			state = state_input
		new_line = task.replace('\x00', '') + "\t" + state + "\n"
		new_lines.append(new_line)
	
	# delete everything in file 
	f.truncate(0)

	f.seek(0)
	# add new lines to file
	f.writelines(new_lines)

def stop_all_processes():
	f= open("tasks.txt","r+")

	# modify tasks.txt
	lines = f.readlines()
	new_lines = []
	for line in lines:
		line = line.split('\t')
		task = line[0].replace('\x00', '')
		state = "off"
		new_line = task.replace('\x00', '') + "\t" + state + "\n"
		new_lines.append(new_line)
	
	# delete everything in file 
	f.truncate(0)

	f.seek(0)
	# add new lines to file
	f.writelines(new_lines)


# set ip adress in db
db.collection(u'configuratie').document(u'config').update({'ip': get_ip_address()})

# ROUTES

# test
@app.route('/test')
def test():
	stop_all_processes()
	update_state("print_1", "running")
	return('Hey, there, SleepyPi')

# gotosleep

@app.route('/gotosleep')
def go_to_sleep():
	stop_all_processes()
	update_state("go_to_sleep", "running")
	return('Hey, there, SleepyPi')

@app.route('/gotosleep/stop')
def go_to_sleep_stop():
	update_state("go_to_sleep", "off")
	return('Hey, there, SleepyPi')

# sleeptracking

@app.route('/sleeptracking')
def sleep_tracking():
	stop_all_processes()
	update_state("sleep_tracking", "running")
	return('Hey, there, SleepyPi')

@app.route('/sleeptracking/stop')
def sleep_tracking_stop():
	update_state("sleep_tracking", "off")
	return('Hey, there, SleepyPi')

@app.route('/sleeptracking/pause')
def sleep_tracking_pause():
	update_state("sleep_tracking", "pause")
	return('Hey, there, SleepyPi')

# alarm

@app.route('/alarm')
def alarm():
	stop_all_processes()
	update_state("alarm", "running")
	return('Hey, there, SleepyPi')

@app.route('/alarm/stop')
def alarm_stop():
	update_state("alarm", "off")
	return('Hey, there, SleepyPi')

# START SERVER
# export FLASK_APP=server.py
# python3 -m flask run --host=0.0.0.0