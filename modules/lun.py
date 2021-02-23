class LUN:
    def __init__ (self , lun_id , lun_bootable ):
        self.id = lun_id
        self.bootable = lun_bootable

    # Print lun properties
    def test(self):
        print(self.id)
        print(self.bootable)

