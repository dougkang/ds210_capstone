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

    def baseline(self):
        request = json.loads(web.data())
        cm = Caffe_Models('baseline')
        return cm.caffe_models_run(request) #response
    
    def style(self):
        request = json.loads(web.data())
        cm = Caffe_Models('style')
        return cm.caffe_models_run(request) #response

    def place(self):
        request = json.loads(web.data())
        cm = Caffe_Models('place')
        return cm.caffe_models_run(request) #response
    
    
#     def baseline(self):
#         request = json.loads(web.data())
#         b = Baseline()
#         respond = b.baseline_run(request)
#         return respond
        
#     def style(self):
#         request = json.loads(web.data())
#         b = Style()
#         respond = b.style_run(request)
#         return respond
        
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