/**
 * Created by leonnguyen on 19/02/2017.
 */
angular.module('scotchApp')
    .factory('dataFactory', ['$http', function ($http) {

        var urlBase = '/';
        var baseApiUrl = '/api';
        var dataFactory = {};

        dataFactory.generateData = function () {
            return $http.get(urlBase + 'generateData');
        };

        dataFactory.login = function (username, hashedPassword) {
            var body = {
                "grant_type": "password",
                "client_id": "android",
                "client_secret": "SomeRandomCharsAndNumbers",
                "username": username,
                "password": hashedPassword
            };
            console.log(body);
            return $http.post(baseApiUrl + '/login', body);
        };

        dataFactory.getAllWorkers = function () {
            return $http.get(baseApiUrl + "/users?userType=Worker");
        };

        dataFactory.getShift = function (shiftId) {
            return $http.get(baseApiUrl + "/shift/" + shiftId);
        };

        //20170327 Khangcv add endShift
        dataFactory.updateShiftTime = function (shiftId, startTime, endTime) {
            console.log(baseApiUrl + "/shift/" + shiftId);
            var data = {};
            data.action = "UpdateTime";

            console.log(startTime);
            console.log(endTime);

            data.shift = {};
            data.shift.startTime = startTime;
            data.shift.endTime = endTime;

            return $http.put(baseApiUrl + "/shift/" + shiftId, data);
        };
        //end

        //20170327 Khangcv add endShift
        dataFactory.endShift = function (shiftId) {

            console.log(baseApiUrl + "/shift/" + shiftId);
            var data = {};
            data.action = "End";
            return $http.put(baseApiUrl + "/shift/" + shiftId, data);
        };
        //end

        //20170327 Khangcv add getShifts
        dataFactory.getShifts = function (status, workerId) {
            console.log(baseApiUrl + "/shift?Status=" + status + "&WorkerId=" + workerId);

            return $http.get(baseApiUrl + "/shift?Status=" + status + "&WorkerId=" + workerId);
        };
        //end

        dataFactory.getCustomer = function (id) {
            return $http.get(urlBase + '/' + id);
        };

        dataFactory.insertCustomer = function (cust) {
            return $http.post(urlBase, cust);
        };

        dataFactory.updateCustomer = function (cust) {
            return $http.put(urlBase + '/' + cust.ID, cust)
        };

        dataFactory.deleteCustomer = function (id) {
            return $http.delete(urlBase + '/' + id);
        };

        dataFactory.getOrders = function (id) {
            return $http.get(urlBase + '/' + id + '/orders');
        };

        return dataFactory;
    }]);