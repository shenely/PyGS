angular.module("kepler", [])
  .directive("svgEarth", function() {
    return {
      restrict: 'E',
      scope: {},
      controller: SVGControl
    };
  })
  .directive("canvasEarth", function() {
    return {
      restrict: 'E',
      scope: {},
      controller: CanvasControl
    };
  })
  .directive("webglEarth", function() {
    return {
      restrict: 'E',
      scope: {},
      controller: WebGLControl
    };
  });

function SVGControl( $scope ) {  
  var color = d3.scale.category10();
  
  var width = 1000,
      height = 500;

  var projection = d3.geo.equirectangular()
      .translate([ width / 2, height / 2])
      .scale(height / Math.PI);

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
  
  var objects = svg.append("g");/*,
      night = objects.append("rect")
          .classed("night", true)
          .attr("width","100%")
          .attr("height","100%"),
      day = objects.append("mask")
          .classed("day", true)
          .attr("id", "mask");*/
  
  /*day.append("rect")
      .classed("dark", true)
      .attr("width","100%")
      .attr("height","100%");
  
  day.append("path")
    .datum({ "name": "sun" })
    .classed("light", true);*/
    
  $scope.objects = {};
  
  var socket = new WebSocket("ws://" + location.host + "/view/global2");
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
  })
}

function CanvasControl( $scope, $element ) {  
  var color = d3.scale.category10();
  
  var width = 1000,
      height = 500;

  var canvas = d3.select($element[0]).append("canvas")
      .attr("width", width)
      .attr("height", height),
      context = canvas.node().getContext("2d");

  var projection = d3.geo.equirectangular()
      .translate([ width / 2, height / 2])
      .scale(500 / Math.PI);

  var path = d3.geo.path()
      .projection(projection)
      .context(context);
  
  var redraw = null;

  d3.json("world-110m.json", function(error, world) {    
    var land = topojson.object(world, world.objects.land),
        border = topojson.object(world, world.objects.countries),
        graticule = d3.geo.graticule();
    
    redraw = function() {
      context.lineWidth = 1.0;
      
      context.beginPath();
      path(graticule.outline());
      context.fillStyle = "#a4bac7";
      context.fill();
      
      context.beginPath();
      path(land);
      context.fillStyle = "#d7c7ad";
      context.fill();
      
      context.beginPath();
      path(border);
      context.strokeStyle = "#a5967e";
      context.stroke();
      
      context.beginPath();
      path(land);
      context.strokeStyle = "#766951";
      context.stroke();
      
      context.globalAlpha = 0.5;
      context.beginPath();
      graticule.lines().map(path);
      context.strokeStyle = "#fff";
      context.lineWidth = 0.5;
      context.stroke();
      
      context.beginPath();
      path(graticule.outline());
      context.strokeStyle = "#fff";
      context.lineWidth = 0.5;
      context.stroke();
      context.globalAlpha = 1.0;
    };
    
    redraw();
  });
    
  $scope.objects = [];
  
  var socket = new WebSocket("ws://" + location.host + "/view/global2");
	socket.onmessage = function (event) {
    var view = JSON.parse(event.data);
    
    redraw();
    
    view.params.states.map(function(d,i) {
      if ($scope.objects.length <= i) $scope.objects.push([]);
  	  $scope.objects[i].push([d.long, d.lat]);
  	  $scope.objects[i].length > 200 ? $scope.objects[i].shift() : null;
    	  
      context.globalAlpha = 0.5;
      context.beginPath();
      path(d3.geo.circle().origin([ d.long, d.lat ]).angle(d.arc)());
      context.fillStyle = color(i);
      context.fill();
      context.globalAlpha = 1.0;
      
      context.beginPath();
      path( { "type": "LineString", "coordinates": $scope.objects[i] } );
      context.strokeStyle = color(i);
      context.lineWidth = 2.0;
      context.stroke();
    });
  };
}

function WebGLControl( $scope, $element ) {  
  var color = d3.scale.category10();
  
  var width = 960,
      height = 500,
      aspect = width / height,
      angle = 70,
      near = 1,
      far = 1000;
      
  var texture = new THREE.Texture(d3.select("canvas-earth").select("canvas").node());

  var scene = new THREE.Scene(),
	    renderer = new THREE.WebGLRenderer( );//{ antialias: true } ),
	    camera = new THREE.PerspectiveCamera(angle, aspect, near, far);
	
	camera.position.z = 2;
	scene.add(camera);
	renderer.setSize(width, height);
	$element[0].appendChild(renderer.domElement);
    
  var geometry = new THREE.SphereGeometry(1, 32, 32),
      material = new THREE.MeshBasicMaterial({ map : texture }),
      mesh = new THREE.Mesh(geometry, material),
      light = new THREE.AmbientLight(0xababab);
	
	scene.add(mesh);
	scene.add(light);
  
  var socket = new WebSocket("ws://" + location.host + "/view/global3");
	socket.onmessage = function (event) {
	  texture.needsUpdate = true;
  };
	
	mesh.rotation.x = Math.PI / 4;
	function animate() {
	  renderer.render(scene, camera);
	  requestAnimationFrame( animate );
	  
	  mesh.rotation.y += Math.PI / 360;
	}
	
	animate();
}
