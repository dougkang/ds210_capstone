import web
import json
# import index

urls = (
    '/', 'index'
)

# class index:
#     def GET(self):
#         return "Hello1, world!"

class index:
    def GET(self):
        pyDict = {'one':1,'two':2}
        web.header('Content-Type', 'application/json')
        return json.dumps(pyDict)

    def POST(self):
#         pyDict = {'one':1,'two':2}
        pyDict = web.input()
        web.header('Content-Type', 'application/json')
        return json.dumps(pyDict)


    
    
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()