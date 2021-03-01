# rhvm
yum install git epel-release -y\
yum install https://resources.ovirt.org/pub/yum-repo/ovirt-release43.rpm\
yum install python-ovirt-engine-sdk4\
yum install python-pip\
wget -O ca1.pem --user $user --password $pass --no-check-certificate  https://rhvmanager02.svt.hn/ovirt-engine/services/pki-resource?resource=ca-certificate&format=X509-PEM-CA\
sudo pip install numpy==1.12.0\
sudo pip install pandas==0.24.2\
sudo pip install xlrd==1.0.0:\

#note: only with 1 ip

