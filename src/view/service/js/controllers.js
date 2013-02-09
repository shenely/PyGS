'use strict';

/* Controllers */


function UniverseControl( $scope, $element, global2d ) {  
	var color = d3.scale.category10();
	  
	var width = 960,
	    height = 500,
	    aspect = width / height,
	    angle = 70,
	    near = 1,
	    far = 1000;
	      
	var texture = new THREE.Texture(d3.select("canvas[earth]").node());
	
	var scene = new THREE.Scene(),
	    renderer = new THREE.WebGLRenderer( ),//{ antialias: true } ),
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
  
	global2d.epoch(function (event) {
		texture.needsUpdate = true;
	});
	
	mesh.rotation.x = Math.PI / 4;
    mesh.rotation.y = -Math.PI / 2;
	function animate() {
		renderer.render(scene, camera);
		requestAnimationFrame( animate );
		  
		//mesh.rotation.y += Math.PI / 360;
	}
	
	animate();
}

function EarthControl( $scope, $element, cartograph ) {
    $scope.width = 1000;
    $scope.height = 500;
    
    $scope.path = cartograph($scope.width, $scope.height);
    
	var canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
		context = canvas.getContext("2d");
	
	$scope.canvases = [];
	
	$scope.redraw = function() {
		$scope.path.context(context);
		
    	context.clearRect(0,0,$scope.width,$scope.height);
		
		$scope.canvases.sort(function(a,b) { return a.z - b.z; });
		
		$scope.canvases.forEach(function(d,i) {
			context.drawImage(d.canvas,0,0);
		});
	};
}

function SunControl( $scope, $element, global2d ) {
    var canvas = d3.select($element[0])
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        sun = d3.geo.circle().angle(90),
        context = canvas.getContext("2d");
    
    $scope.setAlpha = function(alpha) {     
        context.globalAlpha = alpha;
    };
    
    $scope.update = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        context.fillStyle = "#000";
        
        context.beginPath();
        $scope.path(sun());
        context.fill();
        
        $scope.redraw();
    };
    
    global2d.epoch(function(epoch) {        
        sun.origin([ 360 * (epoch / 1000 % 86400) / 86400,
                    180 * Math.asin(Math.sin(Math.PI * 23.4 / 180) * Math.cos(2 * Math.PI * epoch / 1000 / 86400 / 365.25)) / Math.PI]);
        
        $scope.update();
    });

    $scope.canvases.push({ z: 20, canvas: canvas });
    $scope.setAlpha(0.5);
}

function SeaControl( $scope, $element ) {
	var canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
	    context = canvas.getContext("2d");
	
	$scope.setColor = function(color) {		
		context.fillStyle = color;
		
		$scope.update();
	};
	
	$scope.update = function() {
		$scope.path.context(context);
		
		context.fillRect(0,0,$scope.width,$scope.height);
		
		$scope.redraw();
	};

	$scope.canvases.push({ z: -1, canvas: canvas });
	$scope.setColor("rgba(164,186,199,1.0)");
}

function LandControl( $scope, $element, world ) {
	var land = null,
		canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
	    context = canvas.getContext("2d");

	$scope.setColor = function(fill, stroke) {
		context.fillStyle = fill;
		context.strokeStyle = stroke;
		
		$scope.update();
	};
	
	$scope.update = function() {
		$scope.path.context(context);
		
    	context.clearRect(0,0,$scope.width,$scope.height);
		
    	context.lineWidth = 1.0;

		context.beginPath();
		$scope.path(land);
		context.fill();
		context.stroke();
		
		$scope.redraw();
	};
	
	world.success(function(d) {
		land = topojson.object(d, d.objects.land);
		
		$scope.canvases.push({ z: 0, canvas: canvas });
		
		$scope.setColor("rgba(215,199,173,1.0)","rgba(0,0,0,1.0)");
	});
}

function CountriesControl( $scope, $element, world ) {
	var countries = null,
		canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
	    context = canvas.getContext("2d");

	$scope.setColor = function(color) {		
		context.strokeStyle = color;
		
		$scope.update();
	};
	
	$scope.update = function() {
		$scope.path.context(context);
		
    	context.clearRect(0,0,$scope.width,$scope.height);
		
    	context.lineWidth = 0.5;

		context.beginPath();
		$scope.path(countries);
		context.stroke();
		
		$scope.redraw();
	};
	
	world.success(function(d) {
		countries = topojson.mesh(d, d.objects.countries, function(a, b) { return a.id !== b.id; });
		
		$scope.canvases.push({ z: 1, canvas: canvas });
		
		$scope.setColor("rgba(0,0,0,1.0)");
	});
}

function GraticuleControl( $scope, $element ) {
    var graticule = d3.geo.graticule(),
    	canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
		context = canvas.getContext("2d");
    
    $scope.setColor = function(color) {    	
    	context.strokeStyle = color;
    	
    	$scope.update();
    };
    
    $scope.update = function() {
		$scope.path.context(context);
		
    	context.clearRect(0,0,$scope.width,$scope.height);
		
    	context.lineWidth = 0.5;
    	
        context.beginPath();
        graticule.lines().forEach($scope.path);
        context.stroke();
      
        context.beginPath();
        $scope.path(graticule.outline());
        context.stroke();
		
		$scope.redraw();
    	
    };

	$scope.canvases.push({ z: 5, canvas: canvas });
	$scope.setColor("rgba(0,0,0,1.0)");
}

function FootPrintControl( $scope, $element, global2d ) {
    var canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
		context = canvas.getContext("2d"),
		color = d3.scale.category10(),
		feet = [];
    
    $scope.setAlpha = function(alpha) {    	
    	context.globalAlpha = 0.5;
    };
	
	$scope.update = function() {
		$scope.path.context(context);
		
		context.clearRect(0,0,$scope.width,$scope.height);
		
		context.lineWidth = 0.5;
		
		feet.forEach(function(d,i) {			 
			context.beginPath();
			$scope.path(d());
			context.fillStyle = color(i);
			context.fill();
		});
		
		$scope.redraw();
	};
	
	global2d.states(function(states) {
		states.forEach(function(d,i) {
			if (i >= feet.length) {
				feet.push(d3.geo.circle());
			}
			return feet[i].origin([ d.long, d.lat ]).angle(d.arc);
		});
		
		$scope.update();
	});
	
	$scope.canvases.push({ z: 10, canvas: canvas });
	$scope.setAlpha(0.5);
}

function GroundTrackControl( $scope, $element, global2d ) {
    var canvas = d3.select($element[0])
		    .attr("width", $scope.width)
		    .attr("height", $scope.height)
		    .node(),
		context = canvas.getContext("2d"),
		color = d3.scale.category10(),
		tracks = [];
    
    $scope.setAlpha = function(alpha) {    	
    	context.globalAlpha = alpha;
    };
	
	$scope.update = function() {
		$scope.path.context(context);
		
		context.clearRect(0,0,$scope.width,$scope.height);
		
		context.lineWidth = 2.0;
		
		tracks.forEach(function(d,i) {			 
			context.beginPath();
			$scope.path( { "type": "LineString", "coordinates": d } );
		    context.strokeStyle = color(i);
			context.stroke();
		});
		
		$scope.redraw();
	};
	
	global2d.states(function(states) {
		states.forEach(function(d,i) {
			if (i >= tracks.length) {
				tracks.push([]);
			}
			return tracks[i].push([ d.long, d.lat ]);
		});
		
		$scope.update();
	});
	
	$scope.canvases.push({ z: 5, canvas: canvas });
	$scope.setAlpha(1.0);
}
