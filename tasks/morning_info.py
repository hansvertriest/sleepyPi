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


sense = SenseHat()

# variables
TASKNAME = "morning_info"
TPF = 300 # time per frame in ms
time_ms = int(round(time.time() * 1000))
counter = 0
frame = 0
status = 'off'
duration_factor = 60*1000 #minutses
duration = 0.5 * duration_factor # convert to minutes
duration_counter = 0 

weather_frames_amount = {
	"sunny" : 27,
	"rain" : 10,
	"snow" : 10,
}
weather="snow"
weather_fps = 3

mode = "weather"
text_done = True
msg = ""

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

def show_weather():
	global frame
	global weather_frames_amount
	global weather
	global sense

	# reset frames when animation is over
	if frame > weather_frames_amount[weather]:
		frame = 0

	index = str(frame)
	if not len(index) == 2:
		index = '0' + index
	sense.load_image("../animations/" + weather + "/sprite_"+ index +".png")




def on_snapshot(doc_snapshot, changes, read_time):
	global status
	global sound_name
	global duration
	global pygame
	global msg
	global mode

	for doc in doc_snapshot:
		doc_dict = doc.to_dict()
		mode = doc_dict['wakeupAction']
		if mode == "msg":
			msg = doc_dict['msg']
		# else:
			# fetch weather

			

doc_ref = db.collection(u'configuratie').document(u'config')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)


# loop
print(duration)
while True:
	# every loop is approx 0.0001 s
	time.sleep(0.0001)

	# calculate time since last update
	time_delta = int(round(time.time() * 1000)) - time_ms

	# if more time than tpf has passed => DO THE THING JULIE
	if time_delta > TPF:
		counter += 1
		frame += 1
		time_ms = int(round(time.time() * 1000)) # reset time
		
		# timer
		print(duration_counter)
		if duration_counter > duration: 
			print('turning off')
			update_state(TASKNAME, 'off')
			duration_counter = 0

		state = get_state()
		# start
		if state == "running" and status == "off":
			duration_counter += TPF
			status = "playing"
			if mode == 'weather':
				show_weather()
			elif mode == "msg" and text_done:
				sense.show_message(msg)
		# maintain
		elif state == "running" and status == "playing":
			duration_counter += TPF
			if mode == 'weather':
				show_weather()
			elif mode == "msg" and text_done:
				sense.show_message(msg, 0.1, text_colour=[0, 0, 255], back_colour	=[255, 255, 255])
		# #  pause
		# elif state == "pause" and status == "playing":
		# 	pygame.mixer.music.pause()
		# 	sense.clear()
		# 	status = "paused"
		# #  unpause
		# elif state == "running" and status == "paused":
		# 	pygame.mixer.music.unpause()
		# 	status = "playing"
		# stop
		elif state == "off" and status == "playing":
			sense.clear()
			status = "off"