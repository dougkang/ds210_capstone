# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-node-js-application-for-production-on-ubuntu-14-04
sudo apt-get update
sudo apt-get install -y build-essential openssl libssl-dev pkg-config


# cd ~
# wget https://nodejs.org/dist/v4.2.2/node-v4.2.2-linux-x64.tar.gz
# tar xvf node-v*
# cd node-v*
# ./configure
# make
# sudo make install

curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
sudo apt-get install -y nodejs

sudo apt-get install git
sudo npm install pm2 -g


sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 3000

pm2 start hello.js
pm2 stop hello.js

pm2 start /home/ubuntu/ds210_capstone_v2/website/web_ejs app.js
pm2 restart /home/ubuntu/ds210_capstone_v2/website/web_ejs/app.js

pm2 stop /home/ubuntu/ds210_capstone_v2/website/web_ejs app.js

# ssh -i w210_keypair.pem ubuntu@52.90.171.178
# scp -i w210_keypair.pem -r /Users/maktrix/Dropbox/Berkeley/W210_Capstone/ds210_capstone/website/web_ejs ubuntu@52.90.171.178:.