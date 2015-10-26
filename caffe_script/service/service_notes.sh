POST vs GET
http://www.w3schools.com/tags/ref_httpmethods.asp

CURL COMMANDS
http://askubuntu.com/questions/299870/http-post-and-get-using-curl-in-linux

JSON EXAMPLE
http://stackoverflow.com/questions/7172784/how-to-post-json-data-with-curl-from-terminal-commandline-to-test-spring-rest



curl -i -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:3000

curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://localhost:3000/

#CREATE
curl -X POST  -H "Content-Type: application/json" -d '{"title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://localhost:8080/resources/

#UPDATE
curl -X PUT  -H "Content-Type: application/json" -d '{"id":"23", "title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://localhost:8080/resources/23

#DELETE
curl -X DELETE http://localhost:8080/resources/23


curl -X POST  -H "Content-Type: application/json" -d '{"title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://localhost:8080/resources/




