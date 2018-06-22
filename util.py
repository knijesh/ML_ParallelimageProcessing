# #path = '/Users/g01179665/Desktop/PPI Templates/PPI/248778 NORMAL TAPES  - ADAM WINSHIP1'
import os
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import datetime
import time
from keras.models import load_model

def util(path,elements=100000,folder_list=[]):	
	"""
	Wrapper to deal with I/O reading and memory check of data Structure
	"""
	file_list =[]
	labels =[]
	if len(folder_list) == 0 and not len(file_list) > elements:
		for root, dirs, files in os.walk(path):		
		    for i,fil in enumerate(files):
		    	if fil.endswith('tif'):		    	
			    	file_list.append(os.path.join(root,fil))
			    	labels.append(i)
	else:
		folders = os.listdir(path)
		dest_folders = [os.path.join(path,fold) for fold in folders if fold in folder_list]		
		for root, dirs, files in os.walk(path):
			for i,fil in enumerate(files):
				if fil.endswith('tif') and root in dest_folders:
					file_list.append(os.path.join(root,fil))
					labels.append(i)

	return file_list,labels


def chunk_generator(lists, batch_size): 
	"""
	function to chunk the lists into batches
	"""	 
	for i in range(0, len(lists), batch_size):
	    yield lists[i:i + batch_size]


def queue_reader(queue):
	"""
	Function to manipulate the Queue reading
	"""
	results = []
	while True:
	    res=queue.get()
	    #print(res)   	             
	    if (res == '/t'):	    	
	        return results
	    else:
	    	results.append(res) 

def files_concatenate(filenames,dir_name):
	"""
	text concatenation

	"""	
	with open(dir_name, 'w') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				for line in infile:
					outfile.write(line)

def get_timestamp():
	times = (
	datetime.datetime.fromtimestamp(
	    int(time.time())
	).strftime('%Y-%m-%d %H:%M:%S')
	)

	return times.split()[0]