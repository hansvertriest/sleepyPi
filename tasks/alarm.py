import pygame
import time
from sense_hat import SenseHat
import firebase_admin
from firebase_admin import credentials, firestore
import threading

# firebase
cred = credentials.Certificate("../config.json")
firebase_admin.initialize_app(cred)

# connect firestore
db = firestore.client()

# inits
pygame.mixer.init()
sense = SenseHat()


status = 'off'

# framerate
TASKNAME = "alarm"
TPF = 300 # time per frame in ms
time_ms = int(round(time.time() * 1000))
counter = 0
counter_limit = 5
flash_counter = 0
flash_limit = 2

# sound
pygame.mixer.music.set_volume(0.07)
sound_name = "morning"

# timer
duration_factor=60*1000 # convert to minutes
duration = 1 * duration_factor
duration_counter = 0


# functions

def get_state() :
	f= open("../tasks.txt","r")
	task_state = ""
	if f.mode == "r":
		lines = f.readlines()
		for line in lines:
			line = line.split('\t')
			task = line[0]
			state = line[1].replace('\n', '')
			if (task == TASKNAME):
				task_state = state
	f.close();
	return task_state

def update_state(task_input, state_input):
	f= open("../tasks.txt","r+")

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

def show_color():
	global counter
	global counter_limit
	global flash_counter
	global flash_limit

	sense.clear()

				
	X = [0, 100, 255]

	if counter >= counter_limit:
		flash_counter += 1
		X = [255, 255, 255]
		if flash_counter >= flash_limit:
			flash_counter = 0
			counter = 0

	question_mark = [
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	X, X, X, X, X, X, X, X,
	]

	sense.set_pixels(question_mark)

def start_music(filename):
	pygame.mixer.music.load("../sounds/"+filename+".mp3")
	sense.low_light = False
	pygame.mixer.music.play()

def on_snapshot(doc_snapshot, changes, read_time):
	global status
	global sound_name
	global duration
	global pygame

	for doc in doc_snapshot:
		doc_dict = doc.to_dict()
		if not doc_dict["toSleepMusic"] == doc_dict:
			if not sound_name == doc_dict["alarmMusic"]:
				sound_name = doc_dict["alarmMusic"]
				status = "off"
			pygame.mixer.music.set_volume(float(doc_dict['alarmVolume']))

doc_ref = db.collection(u'configuratie').document(u'config')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

# loop

while True:
	time_delta = int(round(time.time() * 1000)) - time_ms
	if time_delta > TPF:
		counter += 1
		time_ms = int(round(time.time() * 1000))
		# timer
		if duration_counter > duration: 
			update_state('alarm', 'off')
			duration_counter = 0

		state = get_state()
		# start
		if state == "running" and status == "off":
			duration_counter += TPF
			start_music(sound_name)
			show_color()
			status = "playing"
		# maintain
		elif state == "running" and status == "playing":
			duration_counter += TPF
			show_color()
		#  pause
		elif state == "pause" and status == "playing":
			pygame.mixer.music.pause()
			sense.clear()
			status = "paused"
		#  unpause
		elif state == "running" and status == "paused":
			pygame.mixer.music.unpause()
			status = "playing"
		# stop
		elif state == "off" and status == "playing":
			pygame.mixer.music.stop()
			sense.clear()
			status = "off"