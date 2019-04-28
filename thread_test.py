import queue


q = queue.Queue()

def inputFunc():
	message = input('Type something man')
	q.put(message, False)
	