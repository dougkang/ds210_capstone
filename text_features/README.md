Server
===

```
usage: server.py [-h] --cfg CFG [--port PORT]

optional arguments:
  -h, --help   show this help message and exit
  --cfg CFG    path to config
  --port PORT  port
```

## Prerequisites

Ensure that you have mongodb installed and running.  You will also need to have
location data pre-loaded.

You will also need to install the prequisites before you can run the server:

```
pip install bottle requests numpy scipy sklearn pymongo
```

## API

### `GET /status` 

- *Description:* Retrieve the status of the server
- *Params*:
  - None
- *Returns*: JSON representing the status of the server

#### Sample Response:
```javascript
{
  "status": "OK"
}
```

### `GET /location/:lid`

- *Description:* Return the recommended locations for this user
- *Params*:
  - `lid`: the location id to look up
- *Returns*: JSON representing the location
  - `latency`: time it took to process request in ms
  - `id`: location id
  - `city`: the name of the city
  - `name`: the name of the airport
  - `lat`: the latitude of the location
  - `long`: the longitude of the location
  - `posts`: posts taken at this location
    - 'src': path to image
    - 'uid': user id of poster
    - 'name': user name of poster
    - 'id': id of post

#### Sample Response:
```javascript
{
  "city": "San Jose",
  "name": "Norman Y Mineta San Jose Intl",
  "latency": 8.383989334106445,
  "country": "United States",
  "posts": [
    {
    "src": "https://path.com/to/image.jpg",
    "uid": "1235678",
    "name": "john.doe",
    "id": "823894781909238_2342342"
    },
    // etc..
  ],
  "long": -121.929022,
  "lat": 37.3626,
  "id": "3574"
}
```

### `GET /predict/:access/:uid`

- *Description:* Return the recommended locations for this user
- *Params*:
  - `access`: the access token to use when extracting the media feed
  - `uid`: the id of the instagram user for whom we want to recommend locations
- *Returns*: JSON representing the recommended locations
  - `latency`: time it took to process request in ms
  - `uid`: the user id for who we are recommending
  - `locations`: the location recommendations
    - 'name': name of location
    - 'score': score (higher is better)

#### Sample Response:
```javascript
{
  "latency": 1155.8010578155518,
  "id": "17550552",
  "locations": [
    {
      "score": 0.19999999999999998,
      "posts": [
        {
        "src": "https://path.com/to/image.jpg",
        "uid": "1235678",
        "name": "john.doe",
        "id": "823894781909238_2342342"
        },
        // etc..
      ],
      "id": 3574,
      "name": "San Jose"
    },
    // etc...
  ]
}
```

Trainer
===

```
usage: trainer.py [-h] --cfg CFG --output OUTPUT [--clean] models [models ...]

positional arguments:
  models           type of model to train

optional arguments:
  -h, --help       show this help message and exit
  --cfg CFG        path to config
  --output OUTPUT  path to model output directory
  --clean          clean dataset file
```
