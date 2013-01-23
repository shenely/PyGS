angular.module("kepler", [])
  .directive("earth", function() {
    return {
      restrict: 'E',
      scope: {},
      controller: KeplerControl
    };
  });

function KeplerControl( $scope, $element ) {  
  var color = d3.scale.category10();
  
  var width = 960,
      height = 500;

  var projection = d3.geo.equirectangular()
      .scale(150);

  var path = d3.geo.path()
      .projection(projection);

  var graticule = d3.geo.graticule();

  var svg = d3.select($element[0]).append("svg")
      .attr("width", width)
      .attr("height", height);

  svg.append("path")
      .datum(graticule.outline)
      .attr("class", "background")
      .attr("d", path);

  svg.append("g")
      .attr("class", "graticule")
    .selectAll("path")
      .data(graticule.lines)
    .enter().append("path")
      .attr("d", path);

  svg.append("path")
      .datum(graticule.outline)
      .attr("class", "foreground")
      .attr("d", path);
  
  var objects = svg.append("g"),
      night = objects.append("rect")
          .classed("night", true)
          .attr("width","100%")
          .attr("height","100%"),
      day = objects.append("mask")
          .classed("day", true)
          .attr("id", "mask");
  
  /*day.append("rect")
      .classed("dark", true)
      .attr("width","100%")
      .attr("height","100%");
  
  day.append("path")
    .datum({ "name": "sun" })
    .classed("light", true);*/
    
  $scope.objects = {};
  
  var socket = new WebSocket("ws://localhost:8080/view");
	socket.onmessage = function (event) {
    var view = JSON.parse(event.data);   
    objects.selectAll("path.cover")
      .data(view.params.states)
      .attr("d", function(d,i) {
    	  $scope.objects[i].push([d.long, d.lat]);
    	  $scope.objects[i].length > 200 ? $scope.objects[i].shift() : null;
    	  return path(d3.geo.circle().origin([ d.long, d.lat ]).angle(d.arc)()); 
    	  })
      .enter().append("path")
      	.classed("cover",true)
        .attr("d", function(d,i) { 
    	    $scope.objects[i] = [[d.long, d.lat]];
    	    return path(d3.geo.circle().origin([ d.long, d.lat ]).angle(d.arc)()); })
        .style("fill", function(d,i) { return color(i); } );
   
    objects.selectAll("path.track")
      .data(view.params.states)
      .attr("d", function(d,i) {
      	  return path( { "type": "LineString", "coordinates": $scope.objects[i] } );
        })
      .enter().append("path")
      	.classed("track",true)
        .attr("d", function(d,i) { 
            return path( { "type": "LineString", "coordinates": $scope.objects[i] } );
    	  })
        .style("stroke", function(d,i) { return color(i); } );
  };

  d3.json("world-110m.json", function(error, world) {
    svg.insert("path", ".graticule")
        .datum(topojson.object(world, world.objects.land))
        .attr("class", "land")
        .attr("d", path);

    svg.insert("path", ".graticule")
        .datum(topojson.mesh(world, world.objects.countries, function(a, b) { return a.id !== b.id; }))
        .attr("class", "boundary")
        .attr("d", path);
  });
  /*$scope.objects = [
    { "name": "sun", "visible": true, "lat": -23, "long": 160, "arc": 90 },
    { "name": "goldstone", "visible": true, "lat": 35, "long": -116, "arc": 25 },
    { "name": "madrid", "visible": true, "lat": 40, "long": -4, "arc": 25 },
    { "name": "canberra", "visible": true, "lat": -35, "long": 148, "arc": 25 },
    { "name": "svalbard", "visible": true, "lat": 78, "long": 15, "arc": 25 },
    { "name": "poker flats", "visible": true, "lat": 65, "long": -147, "arc": 25 },
    { "name": "prince albert", "visible": true, "lat": 53, "long": -105, "arc": 25 },
    { "name": "sioux falls", "visible": true, "lat": 43, "long": -96, "arc": 25 },
    { "name": "cachoeira paulista", "visible": true, "lat": -22, "long": -45, "arc": 25 },
    { "name": "buenos aires", "visible": true, "lat": -34, "long": -58, "arc": 25 },
    { "name": "alice springs", "visible": true, "lat": -23, "long": 133, "arc": 25 },
    { "name": "hobert", "visible": true, "lat": -42, "long": 147, "arc": 25 }
  ];
  
  var DEG_TO_RAD = Math.PI / 180,
      RAD_TO_DEG = 180 / Math.PI,
      cosd = function(x) { return Math.cos(DEG_TO_RAD * x); },
      sind = function(x) { return Math.sin(DEG_TO_RAD * x); },
      atand2 = function(y,x) { return RAD_TO_DEG * Math.atan2(y,x); };
  
  var earth = d3.select($element[0]).append("svg")
          .attr("id", "earth"),
      sea = earth.append("rect")
          .classed("sea", true)
          .attr("width", "100%")
          .attr("height","100%"),
      land = earth.append("g"),
      objects = earth.append("g"),
      night = objects.append("rect")
          .classed("night", true)
          .attr("width","100%")
          .attr("height","100%"),
      day = objects.append("mask")
          .classed("day", true)
          .attr("id", "mask");
  
  var projection = d3.geo.equirectangular()
          .scale(150)
          .translate( [ 480, 250 ] ),
      path = d3.geo.path().projection(projection),
      climate = d3.scale.linear()
          .domain( [ -66-33/60-44/3600, -23-26/60-16/3600, 0, 23+26/60+16/3600, 66+33/60+44/3600 ] )
          .range( [ "#fff", "#bb7", "#070", "#bb7", "#fff" ] ),
      color = d3.scale.category10(),
      coverage = function(d) {
        return path(d3.geo.circle().origin([ d.long, d.lat ]).angle(d.arc)());
      };
  
  day.append("rect")
      .classed("dark", true)
      .attr("width","100%")
      .attr("height","100%");
  
  day.append("path")
    .datum({ "name": "sun" })
    .classed("light", true);
  
  var drag = d3.behavior.drag()
      .on("drag", function(d) {
        var coord = projection.invert([d3.event.x,d3.event.y]);
        d.long = coord[0];
        d.lat = coord[1];
        
        d3.select(this).attr("d",coverage);
      });
  var blah = objects.selectAll("path")
      .data($scope.objects, function(d) { return d.name; } )
      .attr("d",coverage)
      .attr("visibility", function(d) { return d.visible ? "visible" : "hidden"; } )
      .call(drag)
      .on("dblclick", function(d) { 
        $scope.$apply(function() {
          d.visible = !d.visible;
        });
      });
  
  blah.enter().append("path")
      .attr("d",coverage)
      .attr("visibility", function(d) { return d.visible ? "visible" : "hidden"; } )
      .style("fill", function(d,i) { return color(i); } )
      .style("fill-opacity", 0.5)
      .call(drag)
      .on("dblclick", function(d) { 
        $scope.$apply(function() {
          d.visible = !d.visible;
        });
      });
  
  $scope.$watch("objects", function(newVal, oldVal) {
    blah.attr("visibility", function(d) {
      return d.visible ? "visible" : "hidden";
    });
  }, true);

  d3.json("readme.json", function(collection) {          
    land.selectAll("path")
        .data(collection.features)
      .enter().append("path")
        .classed("land", true)
        .attr("d", path)
        .style("fill", function(d,i) { return d == null ? "none" : climate(projection.invert(path.centroid(d))[1]); });
  });*/
}
