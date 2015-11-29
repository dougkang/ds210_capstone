// Core modules
var express = require('express');
var path = require('path');
var bodyParser = require('body-parser');
var app = express();

// Environment variables
app.use(bodyParser.urlencoded());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, './client')));

// Database connection and models loading
require('./server/config/mongoose');

// Routes
require('./server/config/routes')(app);

// Listen to port
app.listen(8000, function() {
	console.log("listening on port 8000");
});