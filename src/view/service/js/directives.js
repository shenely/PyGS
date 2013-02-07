'use strict';

/* Directives */


angular.module('kepler.directives', []).
  directive('global2d', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
  }]).
  directive('global3d', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
  }]).
  directive('local', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
  }]);
