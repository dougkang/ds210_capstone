// require mongoose
var mongoose = require('mongoose');
// require fs for loading the model files
var fs = require('fs');
// require path for getting the models path
var path = require('path');
// connect to the db!
// mongoose.connect('mongodb://localhost/full_MEAN-demo');
mongoose.connect('mongodb://localhost/w210project');
// create a variable that points to the path where all of the models live
var models_path = path.join(__dirname, './../models');
// fancy function that reads all of the files from a specific location (models_path) and then does something (requires) for each of the js files in the location
fs.readdirSync(models_path).forEach(function(file) {
	if(file.indexOf('.js') >= 0) {
		// require all of the js files -- remember that require RUNS the code even if there is no module.exports in the file
		require(models_path + '/' + file);
	}
})