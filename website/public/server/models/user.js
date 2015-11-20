// require mongoose
var mongoose = require('mongoose');

// create our schema
var userSchema = new mongoose.Schema({
	name: String
})

// turn the schema into a model
mongoose.model('User', userSchema);

// we don't need to export anything because require runs the code!!! see the mongoose.js file in the config folder