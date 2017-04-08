/**
 * Created by leonnguyen on 18/02/2017.
 */
// create the controller and inject Angular's $scope


scotchApp.controller('aboutController', function($scope, $rootScope) {
    console.log("About");
    $scope.message = 'Look! I am an about page.';
    $rootScope.hasVisitedAboutPage = true;
});

scotchApp.controller('contactController', function($scope, $location, $rootScope) {
    console.log("Contact");

    if ($rootScope.hasVisitedAboutPage == true) {
        $scope.message = 'Contact us! JK. This is just a demo.';
    }
    else {
        $location.path('/about');
    }
});