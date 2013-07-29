function UniverseController() {
	
}

function PlanetController() {
	
}

function EarthController() {
	
}

function GroundController($scope,$element,cartographService,groundView,testService) {
	$scope.width = 2000;
	$scope.height = 1000;
	
	$scope.path = cartographService($scope.width,$scope.height);
	
	var selection = d3.select($element[0]),
		data = ["background","foreground"],
		chart = groundView($scope.path)
			.width($scope.width)
			.height($scope.height);
	
	selection.call(chart);
	
	$scope.redraw = function () {
		chart.clear();
	
		data.forEach(function (d) {
				selection.selectAll("canvas." + d)
					.each(function () { chart.draw(this); });
			});
	};
}

function BackgroundController($scope,$element,$attrs,backgroundView) {
	var selection = d3.select($element[0]),
		data = Object.keys($attrs).filter(function (d) { return d[0] != "$"; }),
		chart = backgroundView($scope.path)
			.width($scope.width)
			.height($scope.height);
	
	selection.call(chart);
	
	$scope.redraw = function () {
		chart.clear();
	
		data.forEach(function (d) {
				selection.selectAll("canvas." + d)
					.each(function () { chart.draw(this); });
			});
		
		$scope.$parent.redraw();
	};
}

function SeaController($scope,$element,$attrs,seaView) {
	var color = $attrs["sea"] || "rgba(164,186,199,1.0)";
	
	var selection = d3.select($element[0]),
		chart = seaView($scope.path)
			.color(color)
			.width($scope.width)
			.height($scope.height);

	selection.call(chart);
	
	chart.redraw();
	
	$scope.redraw();
}

function LandController($scope,$element,$attrs,topographyService,landView) {
	var color = $attrs["land"] || "rgba(215,199,173,1.0)";
	
	var selection = d3.select($element[0]),
		chart = landView($scope.path)
			.color(color);
	
	selection.call(chart);
	
	topographyService.success(function (d) {
        var land = topojson.feature(d, d.objects.land);
        
        chart.redraw(land);
    	
    	$scope.redraw();
    });
}

function CountriesController($scope,$element,$attrs,topographyService,countriesView) {
	var color = $attrs["border"] || "rgba(0,0,0,1.0)";
	
	var selection = d3.select($element[0]),
		chart = countriesView($scope.path)
			.color(color);
	
	selection.call(chart);
	
	topographyService.success(function (d) {
        var countries = topojson.mesh(d, d.objects.countries, function(a, b) { return a.id !== b.id; });
        
        chart.redraw(countries);
    	
    	$scope.redraw();
    });
}

function GraticuleController($scope,$element,$attrs,graticuleView) {
	var color = $attrs["border"] || "rgba(0,0,0,1.0)";
	
	var selection = d3.select($element[0]),
		chart = graticuleView($scope.path)
			.color(color);
	
	selection.call(chart);
        
    chart.redraw();
	
	$scope.redraw();
}

function ForegroundController($scope,$element,$attrs,foregroundView) {
	var selection = d3.select($element[0]),
		data = Object.keys($attrs).filter(function (d) { return d[0] != "$"; }),
		chart = foregroundView($scope.path)
			.width($scope.width)
			.height($scope.height);

	selection.call(chart);
	
	$scope.redraw = function () {
		chart.clear();
	
		data.forEach(function (d) {
				selection.selectAll("canvas." + d)
					.each(function () { chart.draw(this); });
			});
		
		$scope.$parent.redraw();
	};
}

function FootPrintController($scope,$element,$attrs,epochModel,geographicModel,footPrintView) {
	var selection = d3.select($element[0]),
		chart = footPrintView($scope.path);
	
	selection.call(chart);
	
	epochModel(function () {
		chart.clear();
		
		selection.selectAll("asset")
			.each(function (d) {
				chart.color(d.color).draw(d.foot());
			});
		
		$scope.redraw();
	});

	selection.selectAll("asset")
		.each(function () {
			var asset = d3.select(this),
				name = asset.attr("name"),
				color = asset.attr("color");
			
			geographicModel(name,function (data) {
				asset.datum({
					"name": name,
					"color": color,
					"foot": d3.geo.circle()
						.origin([ data.long, data.lat ])
						.angle(data.arc)
				});
			});
		});
}

function GroundTrackController() {
	
}

function SpaceController() {
	
}

function TrailPathController() {
	
}

function SubPointController() {
	
}

function AssetController() {
	
}