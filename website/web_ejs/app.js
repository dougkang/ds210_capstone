// get all the tools we need
var express  = require('express');
var app      = express();
var port     = process.env.PORT || 3000;
// var mongoose = require('mongoose');
var passport = require('passport');
var flash    = require('connect-flash');
var path = require('path');

var morgan       = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser   = require('body-parser');
var session      = require('express-session');
var request      = require('request');  // for fetching response from http api

var util = require('util')
var InstagramStrategy = require('passport-instagram').Strategy;

var INSTAGRAM_CLIENT_ID = "aa0986f05f244de6b86a3cc3026914d7"
var INSTAGRAM_CLIENT_SECRET = "3da6cb6b62324e6c8fbb19cbc5bfb6e4";


// Passport session setup.
//   To support persistent login sessions, Passport needs to be able to
//   serialize users into and deserialize users out of the session.  Typically,
//   this will be as simple as storing the user ID when serializing, and finding
//   the user by ID when deserializing.  However, since this example does not
//   have a database of user records, the complete Instagram profile is
//   serialized and deserialized.
passport.serializeUser(function(user, done) {
  done(null, user);
});

passport.deserializeUser(function(obj, done) {
  done(null, obj);
});


// Use the InstagramStrategy within Passport.
//   Strategies in Passport require a `verify` function, which accept
//   credentials (in this case, an accessToken, refreshToken, and Instagram
//   profile), and invoke a callback with a user object.
passport.use(new InstagramStrategy({
    clientID: INSTAGRAM_CLIENT_ID,
    clientSecret: INSTAGRAM_CLIENT_SECRET,
    callbackURL: "http://localhost:3000/auth/instagram/callback",
    passReqToCallback: true
  },
  // function(accessToken, refreshToken, profile, done) {
  function(req, accessToken, refreshToken, profile, done) {
    // asynchronous verification, for effect...
    req.session.accessToken = accessToken; //https://groups.google.com/forum/#!topic/passportjs/bVF0fEMDgqM

    process.nextTick(function () {
      // To keep the example simple, the user's Instagram profile is returned to
      // represent the logged-in user.  In a typical application, you would want
      // to associate the Instagram account with a user record in your database,
      // and return that user instead.
      return done(null, profile);
    });
  }
));




var app = express();


// set up our express application
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');
app.use(morgan());
app.use(cookieParser());
app.use(bodyParser.json()); // get information from html forms
app.use(bodyParser.urlencoded({ extended: true }));
// app.use(express.methodOverride());
app.use(session({ secret: 'keyboard cat' }));
// Initialize Passport!  Also use passport.session() middleware, to support
// persistent login sessions (recommended).
app.use(passport.initialize());
app.use(passport.session());
// app.use(app.router);
// app.use(express.static(__dirname + '/public'));
app.use(express.static(path.join(__dirname,"./static")));

app.get('/', function(req, res){
  // console.log(req.isAuthenticated());
  // req.session.destroy(function(err){
    // console.log(req);
    res.render('index', { user: req.user });


 

  // });
});

app.get('/main', ensureAuthenticated, function(req, res){
  // res.render('main', { user: req.user });
  // console.log(req.session.accessToken);
  // console.log(req.user.id);
  var request_url = 'http://dgkng.com:3000/predict/'+req.session.accessToken+'/'+req.user.id;
  // console.log(request_url);  //http://dgkng.com:3000/predict/49795492.aa0986f.971b538159da4711bc1b7bc48defad31/49795492
  request(request_url, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      var locations = JSON.parse(body).locations;
      // console.log(req);
      // for (var i in locations){
      // //   console.log(response[i]);
      //   locations.push(locations[i].name);
      // }
      console.log(locations);
      res.render('main', { user: req.user, locations: locations});
    }
  })
});



// GET /auth/instagram
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  The first step in Instagram authentication will involve
//   redirecting the user to instagram.com.  After authorization, Instagram
//   will redirect the user back to this application at /auth/instagram/callback
app.get('/auth/instagram',
  passport.authenticate('instagram'),
  function(req, res){
    // The request will be redirected to Instagram for authentication, so this
    // function will not be called.
  });

app.get('/auth/instagram',
  passport.authenticate('instagram'),
  function(req, res){
    // The request will be redirected to Instagram for authentication, so this
    // function will not be called.
  });

// GET /auth/instagram/callback
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  If authentication fails, the user will be redirected back to the
//   login page.  Otherwise, the primary route function function will be called,
//   which, in this example, will redirect the user to the home page.
app.get('/auth/instagram/callback', 
  passport.authenticate('instagram', { failureRedirect: '/login' }),
  function(req, res) {
    res.redirect('/main');
  });

app.get('/logout', function(req, res){
  req.logOut();
  req.session.destroy(function(err){
    res.clearCookie('connect.sid');
    res.redirect('/');
  });
});

app.listen(port);


// Simple route middleware to ensure user is authenticated.
//   Use this route middleware on any resource that needs to be protected.  If
//   the request is authenticated (typically via a persistent login session),
//   the request will proceed.  Otherwise, the user will be redirected to the
//   login page.
function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) { return next(); }
  res.redirect('/login')
}
