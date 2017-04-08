scotchApp.controller('homeController', ['$scope', '$location', '$rootScope', '$http', '$cookies', 'dataFactory',
    function ($scope, $location, $rootScope, $http, $cookies, dataFactory) {

        (function () {

            //end
            var treedata_geography = [{
                label: 'Data1',
                children: [{
                    label: 'Canada',
                    children: ['Toronto', 'Vancouver']
                }, {
                    label: 'USA',
                    children: ['New York', 'Los Angeles']
                }, {
                    label: 'Mexico',
                    children: ['Mexico City', 'Guadalajara']
                }]
            }, {
                label: 'Data2',
                children: [{
                    label: 'Venezuela',
                    children: ['Caracas', 'Maracaibo']
                }, {
                    label: 'Brazil',
                    children: ['Sao Paulo', 'Rio de Janeiro']
                }, {
                    label: 'Argentina',
                    children: ['Buenos Aires', 'Cordoba']
                }]
            }];
            $scope.my_data = treedata_geography;


        })();


        // create a message to display in our view
        console.log("Home");
        $scope.message = 'This is a demo';
        console.log($rootScope);


    }]);
