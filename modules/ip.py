class IP:
    def __init__ (self , IP_ADDRESS , NIC_NAME ):
        self.nic = NIC_NAME
        self.ip = IP_ADDRESS
    def test(self):
        print(self.nic)
        print(self.ip)

