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


curl -vX POST  -H "Content-Type: application/json" -d '{"1094301226639611969_1016687101": "https://scontent.cdninstagram.com/hphotos-xfa1/t51.2885-15/e35/12071132_117024925320109_1448778029_n.jpg", "1079932954249514250_1009689594": "https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/11377801_146811182334693_2053033951_n.jpg", "901390003869460339_1016673720": "https://scontent.cdninstagram.com/hphotos-xft1/t51.2885-15/e15/10919675_339630669566407_1560505453_n.jpg", "1091411570335070017_1002181196": "https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/12139791_172476163092798_682238343_n.jpg", "1085670910110935094_1001957249": "https://scontent.cdninstagram.com/hphotos-xfa1/t51.2885-15/e35/11899529_409336062593154_26859144_n.jpg"}
' -i http://119.81.249.157:3000/resources/1


{ u'1094301226639611969_1016687101': [ { id: "n02641379", "name": "gar, garfish, garpike, billfish, Lepisosteus osseus", "score": 4.0775785e-06 }, { id: "n03877472", "name": "pajama, pyjama, pj's, jammies", "score": 4.0775785e-06 } … ], … }

ssh root@119.81.249.157
password: Za6deUYB
nohup python /root/ds210_capstone/caffe_script/service/app.py 3000 &

nohup ./app.py 3000 &






