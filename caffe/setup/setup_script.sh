#Install general dependencies
# http://caffe.berkeleyvision.org/install_apt.html
# https://github.com/BVLC/caffe/wiki/Install-Caffe-on-EC2-from-scratch-(Ubuntu,-CUDA-7,-cuDNN)
sudo apt-get update
sudo apt-get install libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libhdf5-serial-dev protobuf-compiler
sudo apt-get install --no-install-recommends libboost-all-dev

sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential

#CUDA installation
# https://github.com/BVLC/caffe/wiki/Install-Caffe-on-EC2-from-scratch-(Ubuntu,-CUDA-7,-cuDNN)
#http://www.r-tutor.com/gpu-computing/cuda-installation/cuda7.5-ubuntu
#cg1.4xlarge ($2.1 per hour) http://aws.amazon.com/ec2/previous-generation/
#https://aws.amazon.com/ec2/instance-types/
# g2.2xlarge ($0.65 per Hour) https://aws.amazon.com/ec2/pricing/

#OpenBLAS installation
# https://hunseblog.wordpress.com/2014/09/15/installing-numpy-and-openblas/
# http://osdf.github.io/blog/numpyscipy-with-openblas-for-ubuntu-1204-second-try.html
sudo apt-get install git python-dev gfortran
git clone https://github.com/xianyi/OpenBLAS
cd OpenBLAS
make FC=gfortran
sudo make PREFIX=/usr/local/ install
cd ..

#install remaining dependencies
sudo apt-get install libgflags-dev libgoogle-glog-dev liblmdb-dev


#install Anaconda
# https://www.continuum.io/downloads
wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86_64.sh
bash Anaconda-2.3.0-Linux-x86_64.sh
#need to answer yes 
source /root/.bashrc

#install boost.python (already got pip, numpy, and pandas from Anaconda)
pip install --upgrade pip
conda install -c https://conda.anaconda.org/meznom boost-python

#install caffe
cd ~
git clone https://github.com/BVLC/caffe.git
cd caffe
cat python/requirements.txt | xargs -L 1 pip install

#fix VI editor bad cursor behavior
cat <<EOF >> ~/.vimrc
:set nocompatible
set backspace=indent,eol,start
EOF

#add python path
cat <<EOF >> ~/.bashrc

# add caffe path manually
export PYTHONPATH=/root//caffe/python
EOF

source ~/.bashrc

#get latest Makefile.config [NEED CHANGE HERE]
cp Makefile.config.example Makefile.config
vi Makefile.config

#UNCOMMENT...  CPU_ONLY := 1
#CHANGE... BLAS := atlas  ...INTO...   BLAS := open
#UNCOMMENT... ANACONDA_HOME := $(HOME)/anaconda
#UNCOMMENT ... (3 lines all uncomment) 
#PYTHON_INCLUDE := $(ANACONDA_HOME)/include \
#                $(ANACONDA_HOME)/include/python2.7 \
#                $(ANACONDA_HOME)/lib/python2.7/site-packages/numpy/core/include \

#UNCOMMENT:   PYTHON_LIB := $(ANACONDA_HOME)/lib


#Now we build Caffe. Set X to the number of CPU threads (or cores) on your machine.
#Use the command htop to check how many CPU threads you have.
make pycaffe -j2
make all -j2
make test -j2
make distribute


#Test if everything works
./data/mnist/get_mnist.sh
./examples/mnist/create_mnist.sh

#IN CPU MODE
vi examples/mnist/lenet_solver.prototxt
#CHANGE... solver_mode: GPU   ...INTO...   solver_mode: CPU 

./examples/mnist/train_lenet.sh
  
#Setup iPython notebook
# https://thomassileo.name/blog/2012/11/19/setup-a-remote-ipython-notebook-server-with-numpyscipymaltplotlibpandas-in-a-virtualenv-on-ubuntu-server/
cd ~
git clone --recursive https://github.com/ipython/ipython.git
cd ipython
sudo python setup.py install
####  /usr/local/lib/python2.7/dist-packages/ipython-4.1.0_dev.egg-info
mkdir -p ~/.ipython/profile_nbserver
cd ~/.ipython/profile_nbserver
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem

ipython profile create nbserver

python
# Run python and create an encrypted pass string for your notebook server - then substitute it in python_config.py
#       1. python
#            In [1]: from IPython.lib import passwd
#            In [2]: passwd()
#            Enter password: w210
#            Verify password: w210
#            Out[2]: 'sha1:67c9e60bb8b6:9ffede0825894254b2e042ea597d771089e11aed'

#----------

cat <<EOF >> ~/.ipython/profile_nbserver/ipython_config.py
# Notebook server config below
# Kernel config
c.IPKernelApp.pylab = 'inline'  # if you want plotting support always
# Notebook config
c.NotebookApp.certfile = u'/root/.ipython/profile_nbserver/mycert.pem'
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.password = u'sha1:67c9e60bb8b6:9ffede0825894254b2e042ea597d771089e11aed'
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = 443
EOF

# #install dependencies (ALREADY SATISFIED IN ANACONDA)
# pip install pyzmq --install-option="--zmq=bundled"
# pip install Jinja2 tornado jsonschema

cd ~/ipython
#????? sudo python setup.py submodule

cd ~/.ipython/profile_nbserver
ipython notebook --profile=nbserver


#Get data from google
pip install wget

wget -O dataset.tgz https://doc-0s-7s-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/03brf43rbrv66kbqkshkh8cda4thtufr/1445061600000/04532694062044663674/*/0BwWNqvBKi6uTWFhtT0RpRGJWSEE?e=download
tar zxvf dataset.tgz
cd dataset
mkdir images


# http://tleyden.github.io/blog/2014/10/25/running-caffe-on-aws-gpu-instance-via-docker/
# http://playittodeath.ru/how-to-install-caffe-on-mac-os-x-yosemite-10-10-4/


#Setup web.py service
conda install -c https://conda.anaconda.org/dmnapolitano web.py




