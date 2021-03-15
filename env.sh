yum install git epel-release -y
yum install https://resources.ovirt.org/pub/yum-repo/ovirt-release43.rpm -y
yum install python-ovirt-engine-sdk4 -y
yum install python-pip -y

sudo pip install numpy==1.12.0\
sudo pip install pandas==0.24.2\
sudo pip install xlrd==1.0.0:\
sudo pip install configparser
wget -O ca.pem --user $USER_NAME --password $PASSWORD --no-check-certificate $CERTIFICATE 
