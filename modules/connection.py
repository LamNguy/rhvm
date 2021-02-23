from os import environ as env
import logging
import ovirtsdk4 as sdk
import pandas as pd

class Connection:
    def __init__ (self, env=env ):
        self.url = env['URL']
        self.username = env['USER_NAME']
        self.password = env['PASSWORD']
        self.cert_path = env['CERT_PATH']
    def connection(self):
        logging.basicConfig(level=logging.DEBUG, filename='example.log')

        return  sdk.Connection(
                   url=self.url,
                   username=self.username,
                   password=self.password,
                   ca_file=self.cert_path,
                   debug=True,
                   log=logging.getLogger(),
        )

	
    # Print connection properties
    def test(self):
        print(self.url)
        print(self.username)
        print(self.password)
        print(self.cert_path)

    # Print vms 
    def get_vms(self):
	vms_service = self.connection().system_service().vms_service()
	vms = vms_service.list()
	for vm in vms:
		print('{}:{}').format(vm.name,vm.status)
