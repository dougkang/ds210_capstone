// Creating factory and givint it access to $http to send ajex/api calls
myApp.factory('userFactory',function($http){
	var users = [];
	var factory = {};
	// factory.getUsers = function(callback){
	// 	$http.get('/getUsers').success(function(output){
	// 		users = output;
	// 		callback(users);
	// 	});
	// }
	// factory.addUser = function(newUser,callback){
	// 	$http.post('/addUser',newUser).success(function(output){
	// 		newUser._id=output.id; //grab newly created id from the server
	// 		users.push(newUser);
	// 		callback(users);
	// 	});
	// }
	// factory.removeUser = function(indexUser,callback){
	// 	var serverUserID=users[indexUser]._id; //find server's user id
	// 	$http.post('/removeUser',{_id:serverUserID}).success(function(output){
	// 		console.log(output.msg); //output is just a success delete message
	// 		users.splice(indexUser,1);
	// 		callback(users);
	// 	});		
	// }
	// factory.getOneUser = function(indexUser,callback){
	// 		callback(users[indexUser]); //find find user without going to database		
	// }
	// factory.editUser = function(user,indexUser,callback){
	// 	user._id=users[indexUser]._id;
	// 	$http.post('/editUser',user).success(function(output){
	// 		console.log(output.msg); //output is just a success edit message
	// 		users[indexUser]=user;
	// 		callback(user);
	// 	});				
	// }
	return factory;
});