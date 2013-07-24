'use strict';

/* Controllers */


function UniverseControl( $scope, $element, inertial ) {      
    var width = 1600,
        height = 800,
        aspect = width / height,
        angle = 70,
        near = 1000,
        far = 40000;
    
    $scope.scene = new THREE.Scene();
    
    var renderer = new THREE.WebGLRenderer( { canvas: $element[0], antialias: true } ),
        camera = new THREE.PerspectiveCamera(angle, aspect, near, far),
        ambient = new THREE.AmbientLight(0x333333),
        light = new THREE.PointLight(0xffffff);
    
    camera.position.z = 16000;
    camera.add(light);
    $scope.scene.add(ambient);
    $scope.scene.add(camera);
    renderer.setSize(width, height);
    
    var controls = new THREE.TrackballControls( camera );

    controls.rotateSpeed = 1.0;
    controls.zoomSpeed = 1.2;
    controls.panSpeed = 0.8;

    controls.noZoom = false;
    controls.noPan = false;

    controls.staticMoving = true;
    controls.dynamicDampingFactor = 0.3;

    controls.keys = [ 65, 83, 68 ];
    
    //mesh.rotation.x = Math.PI / 4;
    //mesh.rotation.y = -Math.PI / 2;
    function animate() {
        renderer.render($scope.scene, camera);
        requestAnimationFrame( animate );
          
        //mesh.rotation.y += Math.PI / 360;

        controls.update();
    }

    function render() {
        renderer.render( $scope.scene, camera );
    }

    animate();
}

function PlanetControl( $scope, $element ) {
	$scope.scene.add($scope.mesh);
}

function EarthControl( $scope, $element, inertial ) {
    var geometry = new THREE.SphereGeometry(6378, 32, 32),
        texture = new THREE.Texture(d3.select($element[0]).select("[ground]").node()),
        normal = THREE.ImageUtils.loadTexture( "/static/img/srtm_ramp2.world.5400x2700.jpg" ),
        material = new THREE.MeshPhongMaterial({ map : texture, bumpMap: normal, bumpScale: 100 });
    
    $scope.mesh = new THREE.Mesh(geometry, material);
    
    inertial.epoch(function (epoch) {
        texture.needsUpdate = true;
    });
}

function GroundControl( $scope, $element, cartograph ) {
    $scope.width = 2000;
    $scope.height = 1000;
    
    $scope.path = cartograph($scope.width, $scope.height);
    
    var canvas = d3.select($element[0])
            .attr("width", $scope.width)
            .attr("height", $scope.height),
        context = canvas.node().getContext("2d");
    
    $scope.canvases = [];
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        canvas.select("canvas[background]")
           .each(function(d,i) { context.drawImage(this,0,0); });
        
        canvas.select("canvas[foreground]")
           .each(function(d,i) { context.drawImage(this,0,0); });
    };
}

function BackgroundControl( $scope, $element ) {
    var canvas = d3.select($element[0])
            .attr("width", $scope.width)
            .attr("height", $scope.height),
        context = canvas.node().getContext("2d");
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        canvas.selectAll("canvas")
            .filter(function(d,i) { return d != undefined ? d.visible : null; })
            .sort(function(a,b) { return a.z - b.z; })
            .each(function(d,i) { context.drawImage(this,0,0); });
        
        $scope.$parent.redraw();
    };
}

function ForegroundControl( $scope, $element ) {
    var canvas = d3.select($element[0])
            .attr("width", $scope.width)
            .attr("height", $scope.height),
        context = canvas.node().getContext("2d");
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        canvas.selectAll("canvas")
           .filter(function(d,i) { return d != undefined ? d.visible : null; })
           .sort(function(a,b) { return a.z - b.z; })
           .each(function(d,i) { context.drawImage(this,0,0); });
        
        $scope.$parent.redraw();
    };
}

function SeaControl( $scope, $element ) {
    var canvas = d3.select($element[0])
            .datum({ z: -1, visible: true })
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        context = canvas.getContext("2d");
    
    $scope.setColor = function(color) {        
        context.fillStyle = color;
        
        $scope.redraw();
    };
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.fillRect(0,0,$scope.width,$scope.height);
        
        $scope.$parent.redraw();
    };

    $scope.setColor("rgba(164,186,199,1.0)");
}

function LandControl( $scope, $element, world ) {
    var land = null,
        canvas = d3.select($element[0])
            .datum({ z: 0, visible: true })
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        context = canvas.getContext("2d");

    $scope.setColor = function(fill, stroke) {
        context.fillStyle = fill;
        context.strokeStyle = stroke;
        
        $scope.redraw();
    };
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        context.lineWidth = 1.0;

        context.beginPath();
        $scope.path(land);
        context.fill();
        context.stroke();
        
        $scope.$parent.redraw();
    };
    
    world.success(function(d) {
        land = topojson.feature(d, d.objects.land);
                
        $scope.setColor("rgba(215,199,173,1.0)","rgba(0,0,0,1.0)");
    });
}

function CountriesControl( $scope, $element, world ) {
    var countries = null,
        canvas = d3.select($element[0])
            .datum({ z: 1, visible: true })
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        context = canvas.getContext("2d");

    $scope.setColor = function(color) {        
        context.strokeStyle = color;
        
        $scope.redraw();
    };
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        context.lineWidth = 0.5;

        context.beginPath();
        $scope.path(countries);
        context.stroke();
        
        $scope.$parent.redraw();
    };
    
    world.success(function(d) {
        countries = topojson.mesh(d, d.objects.countries, function(a, b) { return a.id !== b.id; });
        
        $scope.setColor("rgba(0,0,0,1.0)");
    });
}

function GraticuleControl( $scope, $element ) {
    var graticule = d3.geo.graticule(),
        canvas = d3.select($element[0])
            .datum({ z: 5, visible: true })
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        context = canvas.getContext("2d");
    
    $scope.setColor = function(color) {        
        context.strokeStyle = color;
        
        $scope.redraw();
    };
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        context.lineWidth = 0.5;
        
        context.beginPath();
        graticule.lines().forEach($scope.path);
        context.stroke();
      
        context.beginPath();
        $scope.path(graticule.outline());
        context.stroke();
        
        $scope.$parent.redraw();
        
    };

    $scope.setColor("rgba(0,0,0,1.0)");
}

function FootPrintControl( $scope, $element, geographic ) {
    var canvas = d3.select($element[0])
            .datum({ z: 20, visible: true })
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        context = canvas.getContext("2d"),
        color = d3.scale.category10(),
        feet = {};
    
    $scope.setAlpha = function(alpha) {        
        context.globalAlpha = 0.5;
    };
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        context.lineWidth = 0.5;
        
        for (name in feet) {           
            context.beginPath();
            $scope.path( feet[name].circle() );
            context.fillStyle = feet[name].data.color;
            context.fill();
        }
        
        $scope.$parent.redraw();
    };
    
    geographic.assets(function(assets) {
    	assets.forEach(function(d,i) {
            if ((d.name in feet) == false) { feet[d.name] = { circle: d3.geo.circle() }; }
            
            feet[d.name].data = d;
            feet[d.name].circle.origin([ d.state.long, d.state.lat ]).angle(d.state.arc);
        });
        
        $scope.redraw();
    });
    
    $scope.setAlpha(0.5);
}

function GroundTrackControl( $scope, $element, geographic ) {
    var canvas = d3.select($element[0])
            .datum({ z: 10, visible: true })
            .attr("width", $scope.width)
            .attr("height", $scope.height)
            .node(),
        context = canvas.getContext("2d"),
        color = d3.scale.category10(),
        tracks = {};
    
    $scope.setAlpha = function(alpha) {        
        context.globalAlpha = alpha;
    };
    
    $scope.redraw = function() {
        $scope.path.context(context);
        
        context.clearRect(0,0,$scope.width,$scope.height);
        
        context.lineWidth = 2.0;
        
        for (name in tracks) {
            context.beginPath();
            $scope.path( tracks[name].path );
            context.strokeStyle = tracks[name].data.color;
            context.stroke();
        }
        
        $scope.$parent.redraw();
    };
    
    geographic.assets(function(assets) {
    	assets.forEach(function(d,i) {
            if ((d.name in tracks) == false) {
                tracks[d.name] = { path: { "type": "LineString", "coordinates": [] } };
            }
            tracks[d.name].data = d;
            tracks[d.name].path.coordinates.push([ d.state.long, d.state.lat ]);
            if (tracks[d.name].path.coordinates.length > 100) {
                tracks[d.name].path.coordinates.shift();
            }
        });
        
        $scope.redraw();
    });
    
    $scope.setAlpha(1.0);
}

function SpaceControl( $scope, $element ) {
}

function TrailPathControl( $scope, $element, inertial ) {
    var color = d3.scale.category10();
    
    var trails = {};
    inertial.assets(function (assets) {
    	assets.forEach(function(d,i) {
            if ((d.name in trails) == false) {
                var geometry = new THREE.Geometry(),
                    vector = new THREE.Vector3(d.state.position.$matrix[0][0],
                            d.state.position.$matrix[0][2],
                            -d.state.position.$matrix[0][1]);
                
                for (var j=0;j<100;j++) { geometry.vertices.push(vector); }
                geometry.verticesNeedUpdate = true;
                
                trails[d.name] = { line: new THREE.Line(geometry,new THREE.LineBasicMaterial({ color: d.color, linewidth: 2 })) };
                trails[d.name].line.dynamic = true;
                
                $scope.scene.add(trails[d.name].line);
            }
            var vector = new THREE.Vector3(d.state.position.$matrix[0][0],
                    d.state.position.$matrix[0][2],
                    -d.state.position.$matrix[0][1]);
            
            trails[d.name].data = d;
            trails[d.name].line.geometry.vertices.push(vector);
            trails[d.name].line.geometry.vertices.shift();
            trails[d.name].line.geometry.verticesNeedUpdate = true;
        });
    });
}

function SpaceCraftControl( $scope, $element, inertial ) {
    var color = d3.scale.category10();
    
    var status = THREE.ImageUtils.loadTexture( "/static/img/status-sprite.png" ),
        state = THREE.ImageUtils.loadTexture( "/static/img/state-sprite.png" ),
    	material1 = new THREE.SpriteMaterial( { map: status, useScreenCoordinates: false, color: 0xffffff } ),
    	material2 = new THREE.SpriteMaterial( { map: state, useScreenCoordinates: false, color: 0xffffff } );
    
    var spacecraft = {};
    inertial.assets(function (assets) {
    	assets.forEach(function(d,i) {
            if ((d.name in spacecraft) == false) {
                spacecraft[d.name] = {
                        status: new THREE.Sprite( material1.clone() ),
                        state: new THREE.Sprite( material2.clone() ),
                        object: new THREE.Object3D()
                };

                spacecraft[d.name].state.scale.set( 400, 400 );
                spacecraft[d.name].state.material.color.setStyle(d.color);
                
                spacecraft[d.name].status.scale.set( 400, 400 );

                spacecraft[d.name].object.add(spacecraft[d.name].state);
                spacecraft[d.name].object.add(spacecraft[d.name].status);
                $scope.scene.add(spacecraft[d.name].object);
                
            }

            spacecraft[d.name].data = d;
        	spacecraft[d.name].status.material.color.setStyle(d.status.type);
            spacecraft[d.name].object.position.x = d.state.position.$matrix[0][0];
            spacecraft[d.name].object.position.y = d.state.position.$matrix[0][2];
            spacecraft[d.name].object.position.z = -d.state.position.$matrix[0][1];
        });
    });
}
