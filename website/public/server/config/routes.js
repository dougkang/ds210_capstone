var users = require('../controllers/users');

module.exports = function(app) {
	app.get('/getUsers',function(req,res){
		users.getUsers(req,res);
	});
	app.post('/addUser',function(req,res){
		users.addUser(req,res);
	});
	app.post('/removeUser', function(req, res) {
		users.removeUser(req,res);
	});
	app.post('/editUser', function(req, res) {
		users.editUser(req, res);
	});
}