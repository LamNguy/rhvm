from modules.vm import *
class Utils:
    def __init__ (self, conn):
        self.conn = conn.connection()
        self.instance_types_service = self.conn.system_service().instance_types_service()
        self.disk_service = self.conn.system_service().disks_service()
        self.vms_service = self.conn.system_service().vms_service()
        
    def create_vm (self, vm):
        print(self.conn)
        vm.test()
        virtual_machine = self.vms_service.list(search='{}'.format(vm.name))[0]
        print(virtual_machine.name)
	disks = self.disk_service.list()
	for disk in disks:
		print(disk.name)
