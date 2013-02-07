'use strict';

/* Controllers */


function Global2DController( $scope, $element ) {  
	  var color = d3.scale.category10();
	  
	  var width = 1000,
	      height = 500;

	  var projection = d3.geo.equirectangular()
	      .translate([ width / 2, height / 2])
	      .scale(height / Math.PI);

	  var path = d3.geo.path()
	      .projection(projection);

	  var graticule = d3.geo.graticule();

	  var svg = d3.select("#global2d").append("svg")
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
	  
	  d3.json("/static/dat/world-110m.json", function(error, world) {
	    svg.insert("path", ".graticule")
	        .datum(topojson.object(world, world.objects.land))
	        .attr("class", "land")
	        .attr("d", path);

	    svg.insert("path", ".graticule")
	        .datum(topojson.mesh(world, world.objects.countries, function(a, b) { return a.id !== b.id; }))
	        .attr("class", "boundary")
	        .attr("d", path);
	  });
	  
	  var g = svg.append("g");
	  var objects = {};
	  
	  var socket = new WebSocket("ws://" + location.host + "/view/global2");
		socket.onmessage = function (event) {
	    var view = JSON.parse(event.data);
	    g.selectAll("path.cover")
	      .data(view.params.states)
	      .attr("d", function(d,i) {
	    	  objects[i].push([d.long, d.lat]);
	    	  objects[i].length > 100 ? objects[i].shift() : null;
	    	  return path(d3.geo.circle().origin([ d.long, d.lat ]).angle(d.arc)()); 
	    	  })
	      .enter().append("path")
	      	.classed("cover",true)
	        .attr("d", function(d,i) { 
	    	    objects[i] = [[d.long, d.lat]];
	    	    return path(d3.geo.circle().origin([ d.long, d.lat ]).angle(d.arc)()); })
	        .style("fill", function(d,i) { return color(i); } );
	   
	    g.selectAll("path.track")
	      .data(view.params.states)
	      .attr("d", function(d,i) {
	      	  return path( { "type": "LineString", "coordinates": objects[i] } );
	        })
	      .enter().append("path")
	      	.classed("track",true)
	        .attr("d", function(d,i) { 
	            return path( { "type": "LineString", "coordinates": objects[i] } );
	    	  })
	        .style("stroke", function(d,i) { return color(i); } );
	  };
}
Global2DController.$inject = [];


function Global3DController() {
}
Global3DController.$inject = [];


function LocalController() {
}
LocalController.$inject = [];
