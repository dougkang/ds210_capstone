import web
import json
from controller import Controller
from caffe_models import Caffe_Models

urls = (
    r'/resources(?:/(?P<resource_id>[0-9]+))?',
    'ResourceController',
)

class ResourceController(Controller):

    def list(self):
        return "list resources", format
    
    #MODELS THAT WE USE    
    def style_flickr(self):
        request = json.loads(web.data())
        cm = Caffe_Models('style_flickr')
        return cm.caffe_models_run(request) #response

    def object_lenet(self):
        request = json.loads(web.data())
        cm = Caffe_Models('object_lenet')
        return cm.caffe_models_run(request) #response
    
    def place_lenet(self):
        request = json.loads(web.data())
        cm = Caffe_Models('place_lenet')
        return cm.caffe_models_run(request) #response
    
    
    #MODELS THAT WE ARE NOT USING

    ## this is the baseline
    def object_imagenet(self):
        request = json.loads(web.data())
        cm = Caffe_Models('object_imagenet')
        return cm.caffe_models_run(request) #response

    def place_cnn(self):
        request = json.loads(web.data())
        cm = Caffe_Models('place_cnn')
        return cm.caffe_models_run(request) #response

    
    
    
## ORIGINAL RESTFUL CONTROLLER
#     def get(self, resource_id):
#         return "retrieved resource", resource_id

#     def create(self):
#         resource = json.loads(web.data())
#         return "created resource", resource

#     def update(self, resource_id):
#         resource = json.loads(web.data())
#         return "updated resource", resource_id, resource

#     def delete(self, resource_id):
#         return "deleted resource", resource_id

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()