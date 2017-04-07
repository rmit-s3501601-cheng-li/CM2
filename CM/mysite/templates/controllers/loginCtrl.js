/**
 * Created by leonnguyen on 18/02/2017.
 */
scotchApp.controller('loginController', ['$scope', '$location', '$rootScope', '$http', '$cookies', 'dataFactory',
    function ($scope, $location, $rootScope, $http, $cookies, dataFactory) {
        console.log("loginController");
        $scope.message = 'Please login with your user name and password';
        $scope.userName = "";
        $scope.password = "";

        $scope.doLogin = function () {
            console.log($scope.userName + "|" + $scope.password);

            var hash = md5($scope.password);
            console.log(hash);

            dataFactory.login($scope.userName, hash).then(function (response) {
                console.log(response.data);
                // $scope.message = response.data.Status;
                var authorizationHeader = 'Bearer ' + response.data.access_token;
                console.log(response.data)
                $cookies.put("AuthorizationHeader", authorizationHeader, null);
                $http.defaults.headers.common['Authorization'] = authorizationHeader;
                $rootScope.currentUserSignedIn = true;
                $location.path('/');
            }, function (error) {
                $scope.message = "Error";
            });


            // $http.defaults.headers.common['Accept'] = 'application/json;odata=verbose';

        };

        $scope.test = function () {

            console.log("Test");

            $http.get("/generateData").then(function (response) {
                console.log(response);
                $scope.message = response.data.Status;
            });
        };

    }]);