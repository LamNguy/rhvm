from modules.connection import * 
from modules.utils import *
import pandas as pd
import ovirtsdk4

PATH_EXCEL = '/home/centos/rhvm/test_data.xlsx'
connection = Connection()

try:
	conn = connection.connection()
	data = pd.read_excel(PATH_EXCEL)
	print('Data shape: {}').format(data.shape)
	print(data.head(1))
	connection.test()
	utils = Utils(conn)	
	print(conn.test(raise_exception = True))  # return true if connect successful
	utils = Utils(conn)
	vms = utils.vms_data(data)
	for vm in vms:
		vm.test()	
except ovirtsdk4.AuthError :
	print('Authentication failed, please check adminrc')
except IOError: 
	print('File data not exists')
except Exception as e:
	print(e)
finally:
	conn.close()


