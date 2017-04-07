/**
 * Created by leonnguyen on 23/03/2017.
 */
scotchApp.controller('shiftController', ['$scope', '$stateParams', '$location', '$rootScope', '$http', '$cookies', 'dataFactory', 'utilFactory',
    function ($scope, $stateParams, $location, $rootScope, $http, $cookies, dataFactory, utilFactory) {

        var STATUS_SHIFT_IS_CREATED = 'Created';
        var STATUS_SHIFT_IS_COMPLETED = 'Completed';
        $scope.shifts = [];
        console.log("currentUserSignedIn: " + $rootScope.currentUserSignedIn);
        // check authorization status for navigating
        var authorizationHeader = $cookies.get("AuthorizationHeader");
        if (authorizationHeader != null) {
            $http.defaults.headers.common['Authorization'] = authorizationHeader;
        } else {
            $location.path('/login');
        }
        // end
        console.log('stateParams: ' + $stateParams.workerId);

        $scope.formatDate = function (val) {

        }

        $scope.workerId = $stateParams.workerId;

        function addShiftS(data, response) {
            var i = 0;
            for (i = 0; i < response.data.length; i++) {
                response.data[i].hours = (response.data[i].endTime - response.data[i].startTime) / (1000 * 60 * 60);
                response.data[i].startTime = utilFactory.formatDate(response.data[i].startTime);
                response.data[i].endTime = utilFactory.formatDate(response.data[i].endTime);
                data.push(response.data[i]);
            }
        }

        //20170327 khangcv add - get all created shifts
        dataFactory.getShifts(STATUS_SHIFT_IS_CREATED, $scope.workerId).then(function (response) {
            console.log("created shifts");
            console.log(response);

            addShiftS($scope.shifts, response);


        }, function (error) {
            $scope.message = "Error";
        });
        //20170327 khangcv add - get all completed shifts
        dataFactory.getShifts(STATUS_SHIFT_IS_COMPLETED, $scope.workerId).then(function (response) {
            console.log("completed shifts");
            console.log(response);

            addShiftS($scope.shifts, response);

        }, function (error) {
            $scope.message = "Error";
        });
        //end

        //20170327 khangcv add - endShift
        $scope.endShift = function (shiftId) {
            dataFactory.endShift(shiftId).then(function (response) {
                var i = 0;
                for (i = 0; i < $scope.shifts.length; i++) {
                    if ($scope.shifts[i]._id == response.data._id) {
                        $scope.shifts.splice(i, 1);
                        $scope.shifts.push(response.data);
                    }
                }

                console.log(response);
            })
            console.log("on click ");
        }
        //end


        //20170327 khangcv add  - check shift status
        $scope.isCompleted = function (status) {
            if (status == STATUS_SHIFT_IS_COMPLETED)
                return true;

            return false;
        }
        //end


        console.log("Shift page: " + $scope.shiftId);
        // create a message to display in our view
        $scope.message = 'This is a working shift';
        console.log($rootScope);


    }]);