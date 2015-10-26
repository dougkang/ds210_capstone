import sys
import json

limit=int(sys.argv[1])
inputname=sys.argv[2]
outputname=sys.argv[3]

output={}
count=0

with open(outputname,'w+') as outputfile:
    with open(inputname,'r') as inputfile:        
        for line in inputfile:

            if count>=limit: break

            post = json.loads(line)

            #read json but need to handle index error as certain lines of JSON has errors
            #during as we attempt to extract the value in image_url
            try:
                feed_id = post['feed'][0]['id']
                image_url = post['feed'][0]['images']['standard_resolution']
                #figure out filename
                output[feed_id]=image_url
                count+=1

            except IndexError:
                print "Index error with line of JSON: ignore and go to next line of JSON"

        outputfile.write(json.dumps(output))