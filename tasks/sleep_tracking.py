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

# VARIABLES

TASKNAME = "sleep_tracking"
status = 'off'

# framerate
TPF = 300 # time per frame in ms
time_ms = int(round(time.time() * 1000))
counter = 0

# color animation
direction = -1
upper_limit = 120
starting_value = upper_limit

# sound 
pygame.mixer.music.set_volume(0.07)
sound_name = "zen"

# timer
duration_factor=60*1000
duration = 0.5 * duration_factor
duration_counter = 0

# dispaly
mode = "colors"

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
	global starting_value
	global counter
	global direction
	global upper_limit

	# clear screen
	sense.clear()

	# determine green value
	g = starting_value + (counter*3) * direction

	# guard limits of green
	if g <= 0 :
		g = 0
		starting_value = 0
		counter = 0
		direction = 1
	if g >= upper_limit:
		g = upper_limit
		starting_value = upper_limit
		counter = 0
		direction = -1

	# set pixels
 
	X = [255, g, 0]

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

def show_red_light():
	# set pixels
	X = [255, 0, 0]

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
	pygame.mixer.music.play()

def on_snapshot(doc_snapshot, changes, read_time):
	global status
	global sound_name
	global duration
	global pygame
	global mode

	for doc in doc_snapshot:
		doc_dict = doc.to_dict()
		# als toSleepMusic has changed 
		if not sound_name == doc_dict["toSleepMusic"]:
			sound_name = doc_dict["toSleepMusic"]
			status = "off"
		# set timer
		duration = int(doc_dict['toSleepTimer'])  * duration_factor
		# set musicVolume
		pygame.mixer.music.set_volume(float(doc_dict['toSleepVolume']))
		# set displaymode
		mode = doc_dict['toSleepDisplay']
		print(mode)

doc_ref = db.collection(u'configuratie').document(u'config')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

# loop

while True:
	# get difference in time
	time_delta = int(round(time.time() * 1000)) - time_ms

	# if difference in time is bigger as the time for one frame
	if time_delta > TPF:
		# increment frame counter
		counter += 1

		# reset time_ms
		time_ms = int(round(time.time() * 1000))

		# timer
		if duration_counter > duration: 
			update_state('sleep_tracking', 'off')
			duration_counter = 0

		state = get_state()
		# start
		if state == "running" and status == "off":
			sense.low_light = True
			duration_counter += TPF
			start_music(sound_name)
			if mode == "colors":
				show_color()
			else:
				show_red_light()
			status = "playing"
		# maintain
		elif state == "running" and status == "playing":
			duration_counter += TPF
			if mode == "colors":
				show_color()
			else:
				show_red_light()
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