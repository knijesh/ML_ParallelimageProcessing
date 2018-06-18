# #path = '/Users/g01179665/Desktop/PPI Templates/PPI/248778 NORMAL TAPES  - ADAM WINSHIP1'
import os
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
from keras.models import load_model

def util(path,elements=100000):	
	"""
	Wrapper to deal with I/O reading and memory check of data Structure
	"""
	file_list =[]
	labels =[]
	for root, dirs, files in os.walk(path):		
	    for i,fil in enumerate(files):	        
	        if not len(file_list)>elements:
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