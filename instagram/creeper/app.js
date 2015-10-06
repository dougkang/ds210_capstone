var assert = require('assert')
var async = require('async')
var express = require('express')
var path = require('path')
var cfg = require('./conf/dev')
var app = express()
var bodyparser = require('body-parser')
var mongo = require('mongodb').MongoClient
var ig = require('instagram-node').instagram()

app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'jade')

app.use(express.static('public'));

app.use(bodyparser.json({}));

var ig_keys = {
  client_id: process.env.INSTAGRAM_CLIENT_ID,
  client_secret: process.env.INSTAGRAM_CLIENT_SECRET 
}

// Now that we've grabbed all the configuration values we could
// possibly imagine, check to see that they are valid
assert.ok(cfg.threshold, "config value threshold not specified")
assert.ok(cfg.port, "config value port not specified")
assert.ok(cfg.mongo, "config value mongo not specified")
assert.ok(cfg.mongo.port, "config value mongo.port not specified")
assert.ok(cfg.mongo.host, "config value mongo.host not specified")
assert.ok(cfg.mongo.collection, "config value mongo.collection not specified")
assert.ok(cfg.mongo.db, "config value mongo.db not specified")
assert.ok(ig_keys.client_id, "INSTAGRAM_CLIENT_ID env variable not specified")
assert.ok(ig_keys.client_secret, "INSTAGRAM_CLIENT_ID env variable not specified")

// Authenticate Instagram API
ig.use(ig_keys)

// Initialize Mongo
// Note that we don't wait for mongo to load before continuing.  This means that
// there might be a small window of time where we might try to access the server
// before mongo is up and running.  That's ok though
var url = 'mongodb://'+cfg.mongo.host+':'+cfg.mongo.port.toString()+'/'+cfg.mongo.db
var db = undefined
mongo.connect(url, function (err, res) { 
  console.log("Connected to database " + url)
  db = res 
})

// Function to save our results to mongo
var save = function(coll, data, done) {
  console.log("Saving " + JSON.stringify(data))
  var coll = db.collection(coll)
  async.parallel(
    data.map(function(d) { return function(cb) { coll.save(d, cb) } }),
    done)
}

// Index endpoint (to make sure everything is good) 
app.get('/', function(req, res) {
  res.render('index');
});

// Challenge Response endpoint required for Instagram subscriptions
app.get('/notify/geo/:id', function(req, res) {
  console.log("Incoming challenge: " + JSON.stringify(req.query))
  var valid = 
    req.query['hub.mode'] == 'subscribe' &&
    req.query['hub.verify_token'] == 'ds210' &&
    req.query['hub.challenge']

  var response = req.query['hub.challenge']

  if (valid) {
    console.log("Valid challenge response!")
    res.status(200).send(response)
  } else {
    console.log("Invalid challenge response...")
    res.status(400).send("Not valid")
  }
})

var count = 0

// Actual Notification endpoint
app.post('/notify/geo/:id', function(req, res) {
  console.log("Incoming notification: " + JSON.stringify(req.body))

  // Update our count value
  var n = req.body instanceof Array ? req.body.length : 0
  count = (count + n) % cfg.threshold
  console.log("Accumulated " + count + " posts so far")

  if (count == 0) {
    // If we hit the threshold, then let's hit instagram for the latest data
    var geo_id = req.body[0].object_id
    console.log("Threshold reached, hitting instagram w/ geo id " + geo_id)
    async.waterfall([
      function(cb) { 
        ig.geography_media_recent(geo_id, { count: cfg.threshold }, 
          function(err, res) { 
            console.log("Instagram response: " + JSON.stringify(res))
            cb(err, res)
          }
        )
      },
      function(res, cb) { save(cfg.mongo.collection, res, cb) }
    ], function(err, res) {
      if (err) {
        console.log("ERROR: could not save notification: " + err)
      } else {
        console.log("Successfully saved notification: " + res)
      }
    })
  }
  // Instagram suggests we return 200 ASAP, so don't worry about
  // waiting for our save to complete and return the result
  res.status(200).send("OK")
})

// Start the server
app.listen(cfg.port, function() {
  console.log("Creeper started, listening on port " + cfg.port)
})
