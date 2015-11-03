Server
===

```
usage: server.py [-h] --cfg CFG [--port PORT]

optional arguments:
  -h, --help   show this help message and exit
  --cfg CFG    path to config
  --port PORT  port
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
  "latency": 259.95802879333496,
  "uid": "2229281274",
  "locations": [
  {
    "score": 0.1538461538461539,
    "name": "GAO"
  },
  {
    "score": 0.09890109890109892,
    "name": "REDSTONE"
  },
  {
    "score": 0.09890109890109892,
    "name": "MECHERIA"
  },
  {
    "score": 0.08791208791208795,
    "name": "CANTON ISLAND"
  }
  // etc...
  ]
}
```
