/**
 * Created by khangcao on 28/3/17.
 */
angular.module('scotchApp')
    .factory('utilFactory', ['$http', function ($http) {


        var utilFactory = {};

        function padValue(value) {
            return (value < 10) ? "0" + value : value;
        }


        utilFactory.getDateFromString = function (strDate) {
            var a = strDate.split(/\/|\s|:/);
            var tmpDate = new Date("20" + a[2], a[0] - 1, a[1], a[3], a[4], "0");
            return tmpDate;
        }

        utilFactory.formatDate = function (dateVal) {
            var newDate = new Date(dateVal);
            var sMonth = newDate.getMonth() + 1;
            var sDay = newDate.getDate();
            var sYear = newDate.getFullYear();
            var sHour = newDate.getHours();
            var sMinute = padValue(newDate.getMinutes());
            var sAMPM = "AM";

            var iHourCheck = parseInt(sHour);

            if (iHourCheck > 12) {
                sAMPM = "PM";
                sHour = iHourCheck - 12;
            }
            else if (iHourCheck === 0) {
                sHour = "12";
            }

            sHour = padValue(sHour);

            var tmp = "" + sYear;
            tmp = tmp.substring(2)

            return sMonth + "/" + sDay + "/" + tmp + " " + sHour + ":" + sMinute + " " + sAMPM;
        }

        //20170327 khangcv add - hours calculation
        utilFactory.getWorkHours = function (startDate, endDate) {
            var sDate = utilFactory.getDateFromString(startDate);
            sDate = sDate.valueOf();
            var eDate = utilFactory.getDateFromString(endDate);
            eDate = eDate.valueOf();

            console.log("hours " + (sDate - eDate) / (1000 * 60 * 60));
            return (sDate - eDate) / (1000 * 60 * 60);
        }

        //end


        return utilFactory;
    }]);