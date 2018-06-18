from check import *
from pred import pred
from util import *
from multiprocessing import Process
from multiprocessing import Pool, Queue
from keras.models import load_model
import tensorflow as tf
import time
import sys, os


def multi_call(path):
	"""
	Multiprocessing function for  parallel processing
	"""
	#tensorflow logging Status
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

	#std flush for memory optimisation
	sys.stdout.flush()

	#multiprocessing Queue
	q= Queue()

	file_list,labels = util(path)
	 
	try:
		file_chunk_list = list(chunk_generator(file_list, 4000))
	except Exception:
		raise AttributeError("Chunking Invalid")	
	try:
		processes = [Process(target=pred, args=(fil, labels, q)) for fil in file_chunk_list]
		for p in processes:			
		    p.start()
		    #print("Process--->{} started".format(p))
		for p in processes:
		    p.join()
		    #print("Process--->{} ended".format(p))

	except Exception as e:		
		print("Process Spawn Error-- {}".format(str(e)))

	try:
		results = queue_reader(q)
		print(results)
	except Exception as e:
		print("Queue reader Error-- {}".format(str(e)))

	return


if __name__ == '__main__':
    start = time.time()
    multi_call(path='C:\\Work\\Barclays\\Sample_Test_images')
    print("Total time taken ---{}".format(time.time() - start))

