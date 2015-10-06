var express = require('express');
var path = require('path');
var cfg = require('./conf/dev');
var app = express();

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade'); 

app.use(express.static('public'));

// TODO doug Better logging
// TODO rosalind Initialize mongo here, put configuration details in conf/dev.js

var save = function(coll, data, cb) {
  // TODO rosalind
  // Implement a save function that, given a json object data, save the object
  // to collection coll and, upon completion, call the function cb
  // cb is a function that takes two arguments: 
  //   1. an error object if an error occurred, otherwise, null
  //   2. the object saved
  cb("Error: Not implemented", null)
}

// Index endpoint (to make sure everything is good) 
app.get('/', function(req, res) {
  res.render('index');
});

// Challenge Response endpoint required for Instagram subscriptions
app.get('/notify/geo/:id', function(req, res) {
  // TODO doug implement this to enable subscriptions
  res.status(500).send("Not implemented")
})

// Actual Notification endpoint
app.post('/notify/geo/:id', function(req, res) {
  console.log("Incoming notification: " + JSON.stringify(req.body))
  save(cfg.mongo.collection, req.body, function(err) {
    if (err) {
      console.log("ERROR: could not save notification: " + err)
      res.status(500).send(err)
    } else {
      console.log("Successfully saved notification")
      res.status(200).send("OK")
    }
  })
})

// Start the server
app.listen(cfg.port, function() {
  console.log("Creeper started, listening on port " + cfg.port)
})
