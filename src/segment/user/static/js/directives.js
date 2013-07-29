angular.module('kepler.directives', [])
	.directive('universe', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: UniverseController
		};
	})
	.directive('planet', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: PlanetController
		};
	})
	.directive('earth', function() {
		return {
			restrict: 'A',
			controller: EarthController
		};
	})
	.directive('ground', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: GroundController
		};
	})
	.directive('background', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: BackgroundController
		};
	})
	.directive('sea', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: SeaController
		};
	})
	.directive('land', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: LandController
		};
	})
	.directive('countries', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: CountriesController
		};
	})
	.directive('graticule', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GraticuleController
		};
	})
	.directive('foreground', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: ForegroundController
		};
	})
	.directive('footPrint', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: FootPrintController
		};
	})
	.directive('groundTrack', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GroundTrackController
		};
	})
	.directive('space', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: SpaceController
		};
	})
	.directive('trailPath', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: TrailPathController
		};
	})
	.directive('subPoint', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: SubPointController
		};
	})
	.directive('asset', function() {
		return {
			restrict: 'E',
			scope: true,
			controller: AssetController
		};
	});