from modules.vm import *
class Utils:
    def __init__ (self, conn):
        self.conn = conn 

    def create_vm (self, vm):
        print(self.conn)
        vm.test()
