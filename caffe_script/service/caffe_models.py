#Grab new images
import ast
import os
import json
import urllib
import posixpath
import urlparse 
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import caffe
import sys

class Caffe_Models():
    
    def __init__(self, model_name):
        if model_name=='style_flickr':
            self.model_path = 'models/finetune_flickr_style/finetune_flickr_style.caffemodel'
            self.model_labels = 'examples/finetune_flickr_style/style_names.txt'
            self.model_deploy='models/finetune_flickr_style/deploy.prototxt'
            self.model_mean='python/caffe/imagenet/ilsvrc_2012_mean.npy'
            self.x_size=227
            self.y_size=227
        elif model_name=='place_lenet':
            self.model_path = 'models/googlenet_places205/googlelet_places205_train_iter_2400000.caffemodel'
            self.model_labels = 'models/placesCNN/categoryIndex_places205.csv'
            self.model_deploy='models/googlenet_places205/deploy_places205.protxt'
            self.model_mean='python/caffe/imagenet/ilsvrc_2012_mean.npy'
            self.x_size=224
            self.y_size=224
        elif model_name=='object_lenet': 
            self.model_path = 'models/bvlc_googlenet/bvlc_googlenet.caffemodel'
            self.model_labels = 'data/ilsvrc12/synset_words.txt'
            self.model_deploy='models/bvlc_googlenet/deploy.prototxt'
            self.model_mean='python/caffe/imagenet/ilsvrc_2012_mean.npy'
            self.x_size=224
            self.y_size=224
#         elif model_name=='object_imagenet':
#             self.model_path ='models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
#             self.model_labels = 'data/ilsvrc12/synset_words.txt'
#             self.model_deploy='models/bvlc_reference_caffenet/deploy.prototxt'
#         elif model_name=='place_cnn':
#             self.model_path = 'models/placesCNN/places205CNN_iter_300000.caffemodel'
#             self.model_labels = 'models/placesCNN/categoryIndex_places205.csv'
#             self.model_deploy='models/placesCNN/places205CNN_deploy.prototxt'
              
        self.index=0
        self.limit=999
        self.num_images=0
        self.num_guesses=5
        self.images = {}
        self.predictions = {}
        self.DATA_PATH = "../../../dataset/"
        self.caffe_root = '../../../caffe/'

    #main function for running the baseline script
    def caffe_models_run(self,request):
        self.generate_image(request)
        self.caffe_setup()
        self.caffe_predict()
        return self.predictions

    #generate images
    def generate_image(self,request):
        #clean up temp file
        for f in os.listdir(self.DATA_PATH+"temp/"):
            os.remove(self.DATA_PATH+"temp/"+f)
           
        #for each feed_id, create image and set index for images
        for feed_id, image_url in request.iteritems():
            
            #read json but need to handle index error as certain lines of JSON has errors
            #during as we attempt to extract the value in image_url
            try:
                #figure out filename
                path = urlparse.urlsplit(image_url).path
                filename = posixpath.basename(path)
                image_path = self.DATA_PATH+"temp/"+filename
                #download to local folder and resize image
                urllib.urlretrieve(image_url,image_path)
                
                #need to handle potential error due to issues not being able to open image file
                try: 
                    img = Image.open(image_path)
                    img.thumbnail((256,256),Image.ANTIALIAS) #best quality
                    #set limit on number of images to process
                    self.index+=1
                    print "file no.",self.index,"processed:",image_path
                    self.images[feed_id]=image_path
                    self.num_images+=1
                    if self.index==self.limit: break
                except IOError:
                    print "Cannot open image: remove image and go to next line of JSON"
                    os.remove(image_path)
                    self.images.pop(feed_id, None)

            except IndexError:
                print "Index error with line of JSON: ignore and go to next line of JSON"
	        self.images.pop(feed_id, None)

                
                
    #Import required modules, set plotting parameters, and run 
    #./scripts/download_model_binary.py models/bvlc_reference_caffenet 
    #to get the pretrained CaffeNet model if it hasn't yet been fetched
    def caffe_setup(self):
        # Make sure that caffe is on the python path:
        sys.path.insert(0, self.caffe_root + 'python')

        plt.rcParams['figure.figsize'] = (10, 10)
        plt.rcParams['image.interpolation'] = 'nearest'
        plt.rcParams['image.cmap'] = 'gray'

#         ##No need to download as Roselind already downloaded the file
#         if not os.path.isfile(self.caffe_root + self.model_path):
# #         if not os.path.isfile(self.caffe_root + 'models/finetune_flickr_style/finetune_flickr_style.caffemodel'):
# #         if not os.path.isfile(self.caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'):
#             print("Downloading pre-trained "+self.model_long_name+" model...")   
# #             print("Downloading pre-trained finetune_flickr_style model...")   
# #             print("Downloading pre-trained CaffeNet model...")       
#             #QUESTIONS... DIDN"T CHANGE!!!
#             os.system(self.caffe_root+"scripts/download_model_binary.py caffe/models/bvlc_reference_caffenet")
        
    #Make image predictions
    def caffe_predict(self):
        
        # Set Caffe to CPU mode, load the net in the test phase for inference, and configure input preprocessing.
        caffe.set_mode_cpu()
        ##CHANGE
        net = caffe.Net(self.caffe_root + self.model_deploy,
                        self.caffe_root + self.model_path,
                        caffe.TEST)
#         net = caffe.Net(self.caffe_root + 'models/finetune_flickr_style/deploy.prototxt',
#                         self.caffe_root + 'models/finetune_flickr_style/finetune_flickr_style.caffemodel',
#                         caffe.TEST)
#         net = caffe.Net(self.caffe_root + 'models/bvlc_reference_caffenet/deploy.prototxt',
#                     self.caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel',
#                     caffe.TEST)


        # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2,0,1))
        ## QUESTION
        transformer.set_mean('data', np.load(self.caffe_root + self.model_mean).mean(1).mean(1)) # mean pixel
        transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
        transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

        # set net to batch size to be the total number of images
        net.blobs['data'].reshape(self.num_images,3,self.x_size,self.y_size)

        
        # load labels
        ##CHANGE
        labels_filename = self.caffe_root + self.model_labels
#         imagenet_labels_filename = self.caffe_root + 'examples/finetune_flickr_style/style_names.txt'
#         imagenet_labels_filename = self.caffe_root + 'data/ilsvrc12/synset_words.txt'
        try:
        ##CHANGE
            labels = np.loadtxt(labels_filename, str, delimiter='\t')
#             labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')
        except:
#             !../data/ilsvrc12/get_ilsvrc_aux.sh
            os.system(self.caffe_root + 'data/ilsvrc12/get_ilsvrc_aux.sh')

        ##CHANGE
            labels = np.loadtxt(labels_filename, str, delimiter='\t')
#             labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')

        # load image data into model
#         for (dirpath, dirnames, filenames) in walk(self.DATA_PATH+"temp/"):
        i=0
        image_ids = {}
        for feed_id, img_path in self.images.iteritems():
            #load image into caffe preprocessor
            net.blobs['data'].data[i] = transformer.preprocess('data',  
                caffe.io.load_image(img_path))
            image_ids[feed_id]=i
            i+=1

        #batch computation step (show computation time)
        net.forward()  # call once for allocation
#         %timeit net.forward()
        
        #display result, showing top 5 prediction for each image
#         for (dirpath, dirnames, filenames) in walk('../../../dataset/images/'):
#             for i,filename in enumerate(filenames):
        for feed_id,i in image_ids.iteritems():
            probs = net.blobs['prob'].data[i].flatten()
            top_probs=probs[-1:-1-self.num_guesses:-1]
            top_k = probs.argsort()[-1:-1-self.num_guesses:-1]
        
            top_predictions = labels[top_k]

            for top_prob,top_prediction in zip(top_probs,top_predictions):
                self.predictions.setdefault(feed_id, [])
                pred_id = top_prediction[:9]
                pred_name = top_prediction[11:]
                self.predictions[feed_id].append({"id":pred_id,"name":pred_name,"score":float(top_prob)}) 
