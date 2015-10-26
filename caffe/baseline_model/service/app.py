import web
import json
from controller import Controller

urls = (
    r'/resources(?:/(?P<resource_id>[0-9]+))?',
    'ResourceController',
)


class ResourceController(Controller):

    def list(self):
        return "list resources", format

    def baseline(self):
        resource = json.loads(web.data())
        return "created resource", resource
        
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