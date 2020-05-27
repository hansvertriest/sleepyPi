from sense_hat import SenseHat
import time

sense = SenseHat()

TASKNAME = "go_to_sleep"
TPF = 50 # time per frame in ms
time_ms = int(round(time.time() * 1000))
counter = 0
frame = 0
direction = -1
upper_limit = 120
starting_value = upper_limit

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

	g = starting_value + ((frame*3)%upper_limit) * direction
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

		
while True:
	time_delta = int(round(time.time() * 1000)) - time_ms
	if time_delta > TPF:
		counter += 1
		time_ms = int(round(time.time() * 1000))

		state = get_state()
		if state == "running":
			# DO THE THING, JULIE
			show_color()
		# elif state == "off":
		# 	sense.clear()

