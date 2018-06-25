import os
import csv,traceback
import pandas as pd
from util import *
#output_path = "./output"

"""
Reconciliation of the index files

"""

def reconcile(output_path,root_path,folder_list):
	try:
		file_list =[]
		for root, dirs, files in os.walk(output_path):
			for f in files:
				if f.endswith(".txt"):
					file_list.append(f)	
		df =[]
		for each in file_list:
			df_1=pd.read_csv(os.path.join(output_path,each),names=["TapeNumber", "Image_Name","OCR Output Index","Status","Action"])
			df.append(df_1)
		result=pd.concat(df,axis=0)
		#Error Files Count Detection from root_path	
		# file_list_original,labels = util(path=root_path,folder_list=folder_list)
		# #print(file_list_original)

		# result["new_file_list"] = result["TapeNumber"].map(str) +os.sep+result["Image_Name"]
		# new_file_list = list(result['new_file_list'])

		# error =[err for err in file_list_original if err not in new_file_list]
		# dirname_filename = [[os.path.dirname(each),os.path.basename(each)] for each in error]

		# #drop new_file list		
		result.to_csv(os.path.join(output_path,'indexfile.csv'),index=False)
		for root, dirs, files in os.walk(output_path):
			for f in files:
				if f.endswith(".txt"):
					os.remove(os.path.join(root,f))

	except Exception as e:
		print(str(traceback.print_exc()))


