import web

class RESTfulController:

    methods = ("list", "get", "create", "update", "delete",
               "update_collection", "delete_collection")

    def __getattr__(self, name):
        if name in self.methods and "headers" in web.ctx:
            raise web.badrequest()
        else:
            raise AttributeError

    def GET(self, resource_id=None):
        if resource_id is None:
            return self.list()
        else:
            return self.get(resource_id)

    def POST(self, resource_id=None):
        if resource_id=="1":
            return 'post_hello1'
#             return self.create()
        elif resource_id=="2":
            return 'post_hello2'
#             raise web.badrequest()


    def PUT(self, resource_id=None):
        if resource_id is None:
            return 'put_hello1'
#             return self.update_collection()
        else:
            return 'put_hello2'
#             return self.update(resource_id)

    def DELETE(self, resource_id=None):
        if resource_id is None:
            return self.delete_collection()
        else:
            return self.delete(resource_id)