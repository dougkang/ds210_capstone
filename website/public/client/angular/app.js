//Setting up the angular app (module)
// var myApp = angular.module('myApp',[]);
var myApp = angular.module('myApp',['ngRoute']);

//partial code goes in here:
// config method to setup routing
myApp.config(function($routeProvider,$locationProvider){
	$routeProvider
		.when('/',{
			templateUrl: 'partials/add.html',
			controller: 'usersListCtrl'
		})
		.when('/edit/:userId',{
			templateUrl: 'partials/edit.html',
			controller: 'usersDetailCtrl'
		})
		.otherwise({
			redirectTo: '/'
		});

		// use the HTML5 History API
    $locationProvider.html5Mode(true);
});
