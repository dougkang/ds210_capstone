# initialize
sudo aptitude update
sudo aptitude safe-upgrade
sudo aptitude install build-essential
# install Node Server
apt-get install curl
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install nodejs
# Git
sudo add-apt-repository ppa:git-core/ppa
sudo apt-get update
sudo apt-get install git
# pull repo from Github and placed core website code into opt folder
git clone https://github.com/dougkang/ds210_capstone
sudo mkdir -p /opt/app/website
sudo cp -r ~/w209_d3_fun/website/web4 /opt/app/website/public
# fix issue with vim editor
cat <<EOF >> ~/.vimrc
:set nocompatible
set backspace=indent,eol,start
EOF
# install node packages
cd /opt/app/website/public
sudo npm install --save
sudo npm install -g nodemon
# # configure node to run 24x7 even when instance die
# sudo cp ~/w209_d3_fun/Admin/node-app.conf /etc/init/
# sudo cat <<EOF >> /etc/init/node-app.conf
# description "App Server"
# author "W210 InstaPlaces Team"

# start on (filesystem and net-device-up IFACE=lo)
# stop on runlevel [!2345]

# respawn

# env PORT=3000

# chdir /opt/app/website/public/
# exec node server.js
# EOF

# # run node, configure nginx and run it
# cd ~/w209_d3_fun/Admin/
# sudo start node-app
# sudo cp ~/w209_d3_fun/Admin/node-app /etc/nginx/sites-available/
# sudo rm /etc/nginx/sites-enabled/default
# sudo ln -s /etc/nginx/sites-available/node-app /etc/nginx/sites-enabled/node-app
# sudo /etc/init.d/nginx restart

