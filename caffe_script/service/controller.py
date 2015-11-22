import web

class Controller:

    methods = ("list", "get", "create", "update", "delete",
               "update_collection", "delete_collection")

    def __getattr__(self, name):
        if name in self.methods and "headers" in web.ctx:
            raise web.badrequest()
        else:
            raise AttributeError

    def POST(self, resource_id=None):
        if resource_id=="1":
            return self.style_flickr()
        elif resource_id=="2":
            return self.object_lenet()
        elif resource_id=="3":
            return self.place_lenet()
        else:
            raise web.badrequest()

## ORIGINAL CRUD OPERATION FROM RESTFUL CONTROLLER            
#     def GET(self, resource_id=None):
#         if resource_id is None:
#             return self.list()
#         else:
#             return self.get(resource_id)
#     #READ - TEST in browswer: http://localhost:8080/resources/23
        
#     def POST(self, resource_id=None):
#         if resource_id is None:
#             return self.create()
#         else:
#             raise web.badrequest()
#     #CREATE - TEST in terminal: curl -X POST  -H "Content-Type: application/json" -d '{"title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://localhost:8080/resources/
    
#     def PUT(self, resource_id=None):
#         if resource_id is None:
#             return self.update_collection()
#         else:
#             return self.update(resource_id)
#     #UPDATE: TEST in terminal: curl -X PUT  -H "Content-Type: application/json" -d '{"id":"23", "title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://localhost:8080/resources/23
    
#     def DELETE(self, resource_id=None):
#         if resource_id is None:
#             return self.delete_collection()
#         else:
#             return self.delete(resource_id)
#     #DELETE: TEST in terminal: curl -X DELETE http://localhost:8080/resources/23