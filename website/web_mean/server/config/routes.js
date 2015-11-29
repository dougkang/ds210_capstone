var users = require('../controllers/users');

// require passport module
var passport = require('passport');
var util = require('util');
var InstagramStrategy = require('passport-instagram').Strategy;

// passport.use(new InstagramStrategy({
//     clientID: 17550552.aa0986f.3ce05672e8ff4e5f8daea918d25ceb43,
//     clientSecret: 17550552,
//     callbackURL: "http://localhost:3000/auth/instagram/callback"
//   },
//   function(accessToken, refreshToken, profile, done) {
//     // asynchronous verification, for effect...
//     process.nextTick(function () {
      
//       // To keep the example simple, the user's Instagram profile is returned to
//       // represent the logged-in user.  In a typical application, you would want
//       // to associate the Instagram account with a user record in your database,
//       // and return that user instead.
//       return done(null, profile);
//     });
//   }
// ));
// http://dgkng.com:3000/predict/17550552.aa0986f.3ce05672e8ff4e5f8daea918d25ceb43/17550552?th=0.002



module.exports = function(app) {

	app.get('/auth/instagram',
	  // passport.authenticate('instagram'),
	  function(req, res){
    // The request will be redirected to Instagram for authentication, so this
    // function will not be called.
    	console.log('test');
  });


	// app.get('/auth/instagram/callback', 
	//   // passport.authenticate('instagram', { failureRedirect: '/login' }),
	//   function(req, res) {
	//     res.redirect('/main');
	//  });




	// app.get('/getUsers',function(req,res){
	// 	users.getUsers(req,res);
	// });
	// app.post('/addUser',function(req,res){
	// 	users.addUser(req,res);
	// });
	// app.post('/removeUser', function(req, res) {
	// 	users.removeUser(req,res);
	// });
	// app.post('/editUser', function(req, res) {
	// 	users.editUser(req, res);
	// });
}