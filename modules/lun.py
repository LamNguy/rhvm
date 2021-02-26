class LUN:

# Class LUN provide information about volume lun
#
#
    def __init__ (self , lun_id , lun_bootable , alias ):
        self.id = lun_id
        self.bootable = lun_bootable
	self.alias = alias

    # Print lun properties
    def test(self):
        print(self.id)
        print(self.bootable)
	print(self.alias)
