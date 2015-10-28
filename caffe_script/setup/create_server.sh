curl 'https://SL543025:atm@api.softlayer.com/rest/v3/SoftLayer_Account/VirtualGuests.json?objectMask=id;hostname;fullyQualifiedDomainName;primaryIpAddress;operatingSystem.passwords' | jq -r '.[] | select(.hostname == "<my_vms_hostname>") | {fullyQualifiedDomainName,id, root_password: .operatingSystem.passwords[] | select(.username == "root").password, primaryIpAddress}'



SL543025


slcli vs create --datacenter=hkg02 --hostname=arthur --os UBUNTU_14_64 --domain=worker.net --billing=hourly --cpu=1 --memory=1028 --key=atm

slcli vs create --datacenter=dal05 --hostname=arthur --os UBUNTU_14_64 --domain=worker.net --billing=hourly --cpu=2 --memory=1028 --key=atm

slcli vs create --datacenter=dal05 --hostname=d3team --os UBUNTU_14_64 --domain=w209.net --billing=hourly --cpu=2 --memory=4096 --key=atm --disk=25



ssh root@119.81.249.157
password: Za6deUYB

https://119.81.249.157

scp root@119.81.249.157:ipython_notebooks/* .
scp root@119.81.249.157:caffe/Makefile.config .
