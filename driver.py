from check import *
from pred import pred
from util import *
from multiprocessing import Process
from multiprocessing import Pool, Queue
from keras.models import load_model
import tensorflow as tf
import time
import sys, os
import logging
import uuid


logger = logging.getLogger(__name__)

logname = "app.log"

if not os.path.exists("./output"):
	os.makedirs("./output")

index_file_path = "./output"

logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



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

	file_list,labels = util(path=path,folder_list=['3'])
	if len(file_list) == 0:
		raise Exception(" No files read..Rerun the driver and check the root path\n")

	try:
		file_chunk_list = list(chunk_generator(file_list,600))
	except Exception:
		raise AttributeError("Chunking Invalid")	
	try:
		processes = [Process(target=pred, args=(fil, labels, q)) for fil in file_chunk_list]
		for p in processes:			
		    p.start()
		    logger.info("Process----{} started".format(p))		    
		    #print("Process--->{} started".format(p))

		try:
			while 1:
				"""
				Queue Synchronization
				"""
				running = any(p.is_alive() for p in processes)
				while not q.empty():
					unique_file_name = str(uuid.uuid4())+".txt"
					results = queue_reader(q)
					with open(os.path.join(index_file_path,unique_file_name),'a+') as f:
						f.write("TapeNumber/FolderName"+"\t\t"+"File Name"+"\t\t"+"OCR Output"+"\n\n")
						for each in results:
							for key, value in each.items():
								f.write(os.path.dirname(key)+"\t"+os.path.basename(key)+"\t"+str(value)+"\n")						

				if not running:
					break

		except Exception as e:
			logger.debug("Queue----{} Error".format(e))
			print("Queue reader Error-- {}".format(str(e)))


		for p in processes:
		    p.join()
		    logger.info("Process----{} ended".format(p))
		    #print("Process--->{} ended".format(p))

	except Exception as e:	
		logger.debug("Process----{} Error".format(p))	
		print("Process Spawn Error-- {}".format(str(e)))

	return


if __name__ == '__main__':
    start = time.time()
    multi_call(path='C:\\Work\Barclays\\Test_B')
    print("Total time taken ---{}".format(time.time() - start))

