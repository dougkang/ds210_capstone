##Instructions to run website on local machine:
Setup Ubuntu 14.04 server
Follow instructios in caffe/setup/setup_script.sh 
(this setup_script.sh will be optimized for easier install)
(will need to add GPU installation instructions)

##Running Caffe with iPython Notebook in the cloud:
####1. Enter the Ubuntu server - this server does not have GPU yet
(Password sent in Slack group)
```
ssh root@119.81.249.157
```
####2. Spin up iPython server 
(MUST do this in '/root' directory). Please enter following commands:
```
cd ~
ipython notebook --profile=nbserver
```
####3. Open up a new web browser and enter this website:
https://119.81.249.157
Please note that you may need to turn off your firewall and proxy. I used Chrome browser and needed to click to confirm I know that I'm going on "unsafe" mode. 

##Location and Status of iPython Notebook
The iPython notebook is located at "~/ipython_notebook" folder. This is being copied to github at "caffe/baseline_model" folder. Please feel free to duplicate and play around with it. 

The current iPython notebook loads in 100 images from Doug's dataset. And the batch of 100 images has been image-processed with display of its top features. 