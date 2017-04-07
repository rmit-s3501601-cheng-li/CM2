/**
 * Created by khangcao on 28/3/17.
 */
scotchApp.controller('shiftDetailController', ['$scope', '$stateParams', '$location', '$rootScope', '$http', '$cookies', 'dataFactory', 'utilFactory', '$window',
    function ($scope, $stateParams, $location, $rootScope, $http, $cookies, dataFactory, utilFactory, $window) {
        var authorizationHeader = $cookies.get("AuthorizationHeader");
        var message = "SUCCESS!";

        if (authorizationHeader != null) {
            $http.defaults.headers.common['Authorization'] = authorizationHeader;
        } else {
            $location.path('/login');
        }
        // end
        console.log('stateParams: ' + $stateParams.shiftId);

        var curShiftId = $stateParams.shiftId;
        //20170327 khangcv add - get shift by id
        dataFactory.getShift(curShiftId).then(function (response) {
            console.log("created shifts");
            console.log(response);
            $scope.shftDetail = response.data;
            //test
            $scope.shftDetail.startTime = utilFactory.formatDate($scope.shftDetail.startTime);
            $scope.shftDetail.endTime = utilFactory.formatDate($scope.shftDetail.endTime);
            //ends

        }, function (error) {
            $scope.message = "Error";
        });

        //20170327 khangcv add - update shift
        $scope.updateShift = function () {

            //convert String Date to Long
            var startTime = utilFactory.getDateFromString($scope.shftDetail.startTime);
            startTime = startTime.valueOf();
            a = $scope.shftDetail.endTime.split(/\/|\s|:/);
            var endTime = utilFactory.getDateFromString($scope.shftDetail.endTime);
            endTime = endTime.valueOf();
            dataFactory.updateShiftTime(curShiftId, startTime, endTime).then(function (response) {
                console.log("update shifts");
                console.log(response);

                $scope.shftDetail = response.data;
                //convert long to  string date
                $scope.shftDetail.startTime = utilFactory.formatDate($scope.shftDetail.startTime);
                $scope.shftDetail.endTime = utilFactory.formatDate($scope.shftDetail.endTime);

                $window.alert(message);

            }, function (error) {
                $scope.message = "Error";
            });
        }
        //end


    }]);