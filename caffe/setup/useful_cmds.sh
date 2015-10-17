slcli vs create --datacenter=hkg02 --hostname=caffe2--os UBUNTU_14_64 --domain=test.net --billing=hourly --cpu=2 --memory=4096 --key=atm --disk=100

slcli vs detail 10570929 --passwords

#list servers
slcli vs list

#list options
slcli vs create-options

#public IP address and the root password of your VS
slcli vs credentials <id>

#delete 

#data centers
http://www.softlayer.com/data-centers


curl 'https://<username>:<api_key>@api.softlayer.com/rest/v3.1/SoftLayer_Product_Order/placeOrder' --data @- | jq -r '.placedOrder.items[] | select(.itemId == 4069) | {id}'