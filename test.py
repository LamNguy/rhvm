from modules.connection import * 
from modules.utils import *
import pandas as pd
import ovirtsdk4
import logging
import os 
import configparser


data_path = os.getcwd() + '/test_data.xlsx'
path = '/vms/vms_test.txt'


connection = Connection()
	
logger = connection.create_logger('result',path)

try:
	conn = connection.connection()
	data = pd.read_excel(data_path)
	#connection.test()
	utils = Utils(conn)	
	if conn.test(raise_exception = True):  # return true if connect successful
		print('Connection success')
	utils = Utils(conn)
	vms = utils.vms_data(data)
	for vm in vms:
		vm.test(logger)	
	print('Check vms_text.txt')
	_exit = raw_input('Press any key to exit')
except ovirtsdk4.AuthError :
	print('Authentication failed, please check adminrc')
except IOError: 
	print('File data not exists')
except Exception as e:
	print(e)
finally:
	conn.close()


