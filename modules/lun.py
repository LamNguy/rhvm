class LUN:

# Class LUN provide information about volume lun
#
#
    def __init__ (self , lun_id , lun_bootable , alias , size ):
        self.id = lun_id
        self.bootable = lun_bootable
	self.alias = alias
	self.size = size

