'use strict';

/* Directives */


angular.module('kepler.directives', [])
	.directive('universe', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: UniverseControl
		};
	})
    .directive('sun', function() {
        return {
            restrict: 'A',
            scope: true,
            controller: SunControl
        };
    })
	.directive('earth', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: EarthControl
		};
	})
	.directive('sea', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: SeaControl
		};
	})
	.directive('land', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: LandControl
		};
	})
	.directive('countries', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: CountriesControl
		};
	})
	.directive('graticule', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GraticuleControl
		};
	})
	.directive('footPrint', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: FootPrintControl
		};
	})
	.directive('groundTrack', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GroundTrackControl
		};
	});
