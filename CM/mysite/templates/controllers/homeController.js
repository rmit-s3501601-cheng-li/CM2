/**
 * Created by leonnguyen on 20/02/2017.
 */
scotchApp.controller('homeController', ['$scope', '$location', '$rootScope', '$http', '$cookies', 'dataFactory',
    function ($scope, $location, $rootScope, $http, $cookies, dataFactory) {

        (function () {
            console.log("currentUserSignedIn: " + $rootScope.currentUserSignedIn);
            //check authorization status for navigating
            var authorizationHeader = $cookies.get("AuthorizationHeader");
            if (authorizationHeader != null) {
                $http.defaults.headers.common['Authorization'] = authorizationHeader;
            } else {
                $location.path('/login');
            }
            //end
            $scope.workers = [];

            dataFactory.getAllWorkers().then(function (response) {
                console.log(response.data);
                $scope.workers = response.data;

            }, function (error) {
                $scope.message = "Error";
            });


        })();


        // create a message to display in our view
        console.log("Home");
        $scope.message = 'This is a list of all the workers';
        console.log($rootScope);


    }]);
