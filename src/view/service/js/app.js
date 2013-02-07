'use strict';


// Declare app level module which depends on filters, and services
angular.module('kepler', ['kepler.filters', 'kepler.services', 'kepler.directives']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/global2d', {templateUrl: 'partials/global2d.html', controller: Global2DController});
    $routeProvider.when('/global3d', {templateUrl: 'partials/global3d.html', controller: Global3DController});
    $routeProvider.when('/local', {templateUrl: 'partials/local.html', controller: LocalController});
    $routeProvider.otherwise({redirectTo: '/global2d'});
  }]);
