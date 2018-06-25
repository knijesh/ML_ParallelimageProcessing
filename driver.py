from check import *
from pred import pred
from util import *
from multiprocessing import Process
from multiprocessing import Pool, Queue
from keras.models import load_model
from reconcile import reconcile
import tensorflow as tf
import time
import sys, os
import logging
import uuid
import configparser
import traceback

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



def multi_call(path,folder_list,chunk_size):
	"""
	Multiprocessing function for  parallel processing
	"""
	#tensorflow logging Status
	logging.info("tensorflow logging Status set to 2")
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

	#std flush for memory optimisation
	sys.stdout.flush()
	logging.info("std flush for memory optimisation")

	#multiprocessing Queue
	q= Queue()

	file_list,labels = util(path=path,folder_list=folder_list)
	logging.info("File_list and labels generated")

	if len(file_list) == 0:
		logging.error("No files read..Rerun the driver and check the root path\n")
		raise Exception(" No files read..Rerun the driver and check the root path\n")

	try:
		file_chunk_list = list(chunk_generator(file_list,chunk_size))
		logging.info("file_chunks created")
	except Exception:
		logging.error("Chunking Invalid\n")
		raise AttributeError("Chunking Invalid")	
	try:
		processes = [Process(target=pred, args=(fil, labels, q)) for fil in file_chunk_list]
		for p in processes:			
		    p.start()
		    logger.info("{}".format(p))		    
		    #print("Process--->{} started".format(p))


		try:			
			
			while 1:
				"""
				Queue Synchronization

				"""				
				running = any(p.is_alive() for p in processes)
				while not q.empty():
					logging.info("Queue Synchronization")
					unique_file_name = str(get_timestamp())+"__"+str(uuid.uuid4())+".txt"
					results = queue_reader(q)
					with open(os.path.join(index_file_path,unique_file_name),'a+') as f:
						logging.info("Writing of index files")
						#f.write("TapeNumber"+"\t\t"+"Image_Name"+"\t\t"+"OCR Output Index"+"\n\n")
						for each in results:
							for key, value in each.items():
								f.write(os.path.dirname(key)+","+os.path.basename(key)+","+str(value)+","+"Success"+"\n")						

				if not running:
					logging.error("Processes not running")
					break

		except Exception as e:
			logger.debug("Queue----{} Error".format(traceback.print_exc()))
			while 1:
				raise Exception("Queue reader Error-- {}".format(str(traceback.print_exc())))
				break



		for p in processes:
		    p.join()
		    logger.info("{}".format(p))
		    #print("Process--->{} ended".format(p))

	except Exception as e:	
		logger.debug("Process----{} Error".format(traceback.print_exc()))	
		print("Process Spawn Error-- {}".format(str(traceback.print_exc())))

	return


if __name__ == '__main__':
	start = time.time()
	#ConfigParser for fetching the parameters from .ini file

	config_file_path  = "config.ini"
	config = configparser.ConfigParser()
	config.read(config_file_path)

	root_path = config.get('root_path','root_path')
	chunk_size = int(config.get('chunk_process','chunk_size'))
	folder_list = config.get('folder_selection','folder_list')
	output_path_reconcile = config.get('root_path','output_path_reconcile')

	multi_call(path=root_path,folder_list=folder_list,chunk_size=chunk_size)

	#####
	#Reconciliation Cycle Uniprocess based

	reconcile(output_path_reconcile,root_path,folder_list)

	print("Total time taken ---{}".format(time.time() - start))
