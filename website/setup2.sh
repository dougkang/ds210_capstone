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

# scp -i w210_keypair.pem -r /Users/maktrix/Dropbox/Berkeley/W210_Capstone/ds210_capstone/website/web_ejs ubuntu@52.90.171.178:.