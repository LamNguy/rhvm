from modules.connection import * 
from modules.utils import *
import pandas as pd
import ovirtsdk4
import multiprocessing
from multiprocessing import  TimeoutError , cpu_count 
from multiprocessing.pool import ThreadPool	
import logging
import os

PATH_EXCEL = os.getcwd() + '/test_data.xlsx'

connection = Connection()
logger = logging.getLogger('result')
filename = os.getcwd() + '/vms/results'
formatter = logging.Formatter(
      '%(asctime)s - %(name)s - Level:%(levelname)s - %(message)s')
handler = logging.FileHandler(filename, mode='w')
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
	conn = connection.connection()
	data = pd.read_excel(PATH_EXCEL)
	utils = Utils(conn)	
	conn.test(raise_exception = True)  # return true if connect successful
	utils = Utils(conn)
	pool = ThreadPool(processes=cpu_count())
	vms = utils.vms_data(data)
        res = pool.map(utils.create_vm, vms)	
	for i in res:
		message = 'Vm {}:{}'.format(i['name'],i['status'])	
		logger.info(message)
	print('Done')
except ovirtsdk4.AuthError :
	print('Authentication failed, please check adminrc')
except IOError: 
	print('File data not exists')
	print(e)
except Exception as e:
	print(e)
finally:
	pool.close()
	pool.join()
	conn.close()


