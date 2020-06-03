from sense_hat import SenseHat
import time

sense = SenseHat()

# VARIABLES

TASKNAME = "go_to_sleep"

# framerate
TPF = 50 # time per frame in ms
time_ms = int(round(time.time() * 1000))
counter = 0
frame = 0
direction = -1
upper_limit = 120
starting_value = upper_limit
status="off"

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

def show_color():
	global starting_value
	global counter
	global frame
	global direction
	global upper_limit

	sense.clear()
				
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

		
while True:
	# get difference in time
	time_delta = int(round(time.time() * 1000)) - time_ms

	# if difference in time is bigger as the time for one frame
	if time_delta > TPF:
		# increment frame counter
		counter += 1

		# reset time_ms
		time_ms = int(round(time.time() * 1000))

		state = get_state()
		if state == "running" and status == "off":
			sense.low_light = True
			show_color()
			status = "running"
		elif state == "off" and status == "running":
			sense.clear()
			status = "off"
			print("Turning off")

