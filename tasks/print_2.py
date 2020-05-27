

TASKNAME = "print_2"

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
		
while True:
	state = get_state()
	if state == "running":
		print "2"
