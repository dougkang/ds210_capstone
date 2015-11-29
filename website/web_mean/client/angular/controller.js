// myApp.controller('usersListCtrl', function($scope,userFactory){
myApp.controller('ctrl', function($scope,userFactory){
	$scope.users = [];

	


	// userFactory.getUsers(function(data){
	// 	$scope.users = data;
	// });
	// $scope.addUser = function(){
	// 	userFactory.addUser($scope.newUser, function(data){
	// 		$scope.users = data;
	// 	});
	// 	$scope.newUser={};
	// }
	// $scope.removeUser = function(user){
	// 	userFactory.removeUser($scope.users.indexOf(user),function(data){
	// 		$scope.users = data;
	// 	});
	// }
});

// myApp.controller('usersDetailCtrl', function($scope,$routeParams,userFactory){
// 	$scope.user = {};
// 	userFactory.getOneUser($routeParams.userId,function(data){
// 		$scope.user = data;
// 	});
// 	$scope.editUser = function(){
// 		userFactory.editUser($scope.changeUser,$routeParams.userId,function(data){
// 			$scope.user = data;
// 		});
// 		$scope.changeUser = {};
// 	}
// });
