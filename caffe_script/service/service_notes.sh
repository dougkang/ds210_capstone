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

curl -X POST  -H "Content-Type: application/json" -d '{"title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://119.81.249.157:3000/resources/1


curl -X PUT  -H "Content-Type: application/json" -d '{"id":"23", "title":"a title","description":"a description","type":"a type","author":"an author"}' -i http://119.81.249.157:3000/resources/23

curl -vX POST  -H "Content-Type: application/json" -d @query.json -i http://119.81.249.157:3000/resources/1

curl -vX POST  -H "Content-Type: application/json" -d '{"1094301226639611969_1016687101": "https://scontent.cdninstagram.com/hphotos-xfa1/t51.2885-15/e35/12071132_117024925320109_1448778029_n.jpg", "1079932954249514250_1009689594": "https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/11377801_146811182334693_2053033951_n.jpg", "901390003869460339_1016673720": "https://scontent.cdninstagram.com/hphotos-xft1/t51.2885-15/e15/10919675_339630669566407_1560505453_n.jpg", "1091411570335070017_1002181196": "https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/12139791_172476163092798_682238343_n.jpg", "1085670910110935094_1001957249": "https://scontent.cdninstagram.com/hphotos-xfa1/t51.2885-15/e35/11899529_409336062593154_26859144_n.jpg"}
' -i http://119.81.249.157:3000/resources/1



#copy remote query file to local
scp root@119.81.249.157:dataset/query.json .


#format that doug wants
{ u'1094301226639611969_1016687101': [ { id: "n02641379", "name": "gar, garfish, garpike, billfish, Lepisosteus osseus", "score": 4.0775785e-06 }, { id: "n03877472", "name": "pajama, pyjama, pj's, jammies", "score": 4.0775785e-06 } … ], … }` 

apt-get install dsniff
tcpkill -i eth0 host 119.81.249.157 and port 3000

sudo netstat -ap | grep 3000
kill <pid>
kill -9 <pid>






