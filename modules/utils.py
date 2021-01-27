from modules.vm import *
import ovirtsdk4.types as types
import time
class Utils:
    def __init__ (self, conn):
        self.conn = conn.connection()
        self.instance_types_service = self.conn.system_service().instance_types_service()
        self.disk_service = self.conn.system_service().disks_service()
        self.vms_service = self.conn.system_service().vms_service()
        self.clusters_service = self.conn.system_service().clusters_service()
	self.profiles_service = self.conn.system_service().vnic_profiles_service()
	
    def list_network (self, _cluster):
	cluster = self.clusters_service.list(search='name={}'.format(_cluster))[0]
	cluster_service = self.clusters_service.cluster_service(cluster.id)
	networks_service = cluster_service.networks_service()
	networks = networks_service.list()
	for network in networks:
		print(network.name)

    def create_vm (self, vm):
 	cpu = types.CpuTopology( cores=vm.vcpu )
	_vm = self.vms_service.add(
			types.Vm(
				name=vm.name,
				memory=vm.ram*1024*1024*1024,
				cpu=types.Cpu(topology=cpu),
				cluster=types.Cluster(
					name=vm.cluster,
				),
				template=types.Template(
					name='ubuntu-18.04',
				),
			),
		)	
	    
	vm_service = self.vms_service.vm_service(_vm.id)


	# add nic in "ovirtmgmt" management network
	_network = 'ovirtmgmt'
	nics_service = vm_service.nics_service()
        profile_id = None

        for profile in self.profiles_service.list():
                if profile.name == _network:
                        profile_id = profile.id
                        break
        for ip in vm.ips:
		nics_service.add(
			types.Nic(
				name=ip.nic,
				interface=types.NicInterface.VIRTIO,
				vnic_profile=types.VnicProfile(id=profile_id)
			),
		)
	
	#
	#  ADD DISK 
	#
	for lun in vm.luns:
		print(lun.id)
		print(lun.bootable) 
		x = self.disk_service(search='id={}'.format(lun.id))
		print(x)
	#disk_attachments_service = vm_service.disk_attachments_service()
	
