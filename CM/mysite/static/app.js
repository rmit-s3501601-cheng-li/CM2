// create the module and name it scotchApp
var scotchApp = angular.module('scotchApp', ['ngCookies', 'ui.router', 'angularBootstrapNavTree']);

scotchApp.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider.state({
        name: 'home',
        url: '/',
        cache: false,
        templateUrl: 'static/pages/home.html',
        controller: 'homeController'
    });
    $stateProvider.state({
        name: 'about',
        url: '/about',
        cache: false,
        templateUrl: 'static/pages/about.html',
        controller: 'aboutController'
    });
    $stateProvider.state({
        name: 'contact',
        url: '/contact',
        cache: false,
        templateUrl: 'static/pages/contact.html',
        controller: 'contactController'
    });
    $stateProvider.state({
        name: 'login',
        url: '/login',
        cache: false,
        templateUrl: 'static/pages/login.html',
        controller: 'loginController'
    });
    $stateProvider.state({
        name: 'users',
        url: '/users',
        cache: false,
        templateUrl: 'static/pages/users.html',
        controller: 'userController'
    });
    //shiftDetail page
    $stateProvider.state({
        name: 'shiftDetail',
        url: '/shiftDetail/:shiftId',
        cache: false,
        templateUrl: 'static/pages/shiftEdit.html',
        controller: 'shiftDetailController'
    });
    // if none of the above states are matched, returned to login page
    $urlRouterProvider.otherwise('/');
});

scotchApp.run(function ($rootScope, $http, $cookies) {
    //20170314 khangcv refresh page
    $rootScope.currentUserSignedIn = false;

    if ($cookies.get("AuthorizationHeader")) {

        $http.defaults.headers.common['Authorization'] = 'Bearer ' + $cookies.get("AuthorizationHeader");
        $rootScope.currentUserSignedIn = true;
        console.log("currentUserSignedIn: " + $rootScope.currentUserSignedIn);
    }

    //end

    console.log("App run");
    $rootScope.hasVisitedAboutPage = false;


    //20170314 khangcv add Logout function
    $rootScope.doLogout = function () {
        console.log('Logout function');
        $rootScope.currentUserSignedIn = false;
        //delete $rootScope.currentUser.name;
        //delete $http.defaults.headers.common['Authorization'];
        $cookies.remove("AuthorizationHeader");

    }
    //end


    console.log($rootScope);
});
