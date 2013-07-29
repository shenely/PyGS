angular.module('kepler.services', [])
	.factory("cartographService", function () {
		return function (width,height) {
			var projection = d3.geo.equirectangular()
				    .translate([width / 2, height / 2])
				    .scale(height / Math.PI);
			
			return d3.geo.path().projection(projection);
		};
	})
	.factory("topographyService", function ($http) {
		return $http.get("/static/dat/world-110m.json");
	})
	.factory("epochModel", function () {
		var socket = new WebSocket("ws://" + location.host + "/sub/system/clock/epoch"),
			callbacks = [];
		
		socket.onmessage = function (message) {
			var epoch = JSON.parse(message.data);
			
			callbacks.forEach(function (callback) { callback(epoch); });
		};
		
		return function (callback) { callbacks.push(callback); };
	})
	.factory("productModel", function () {
		var sockets = {},
			callbacks = {};
		
		return function (name,callback) {
			if (!(sockets[name])) {
				sockets[name] = new WebSocket("ws://" + location.host + "/sub/" + name.toLowerCase() + "/ground/product");
			
				sockets[name].onmessage = function (message) {
					var product = JSON.parse(message.data);
					
					callbacks[name].forEach(function (callback) { callback(product); });
				};
			}
			
			callbacks[name] = callbacks[name] || [];
			callbacks[name].push(callback);
		};
	})
	.factory("geographicModel", [
        "productModel",
        function (productModel) {        	
        	return function (name,callback) {
        		productModel(name,function (product) {
        			if (product.type == 21) {
        				callback(product.data);
        			}
        		});
        	};
        }
	])
	.factory("assetModelService", function () {
		var socket = new WebSocket("ws://" + location.host + "/pub/system/asset/model"),
			queue = [];
		
		socket.onopen = function () {
			while (queue.length > 0) {
				socket.send(queue.pop());
			}
		}
     	
     	return function (model) {
     		var message = JSON.stringify(model);
     		
     		if (socket.readyState != 1) {
     			queue.push(message);
     		} else {
         		socket.send(message);
     		}
     	};
     })
	.factory("assetControllerService", function () {
		var socket = new WebSocket("ws://" + location.host + "/pub/system/asset/controller"),
			queue = [];
		
		socket.onopen = function () {
			while (queue.length > 0) {
				socket.send(queue.pop());
			}
		}
     	
     	return function (controller) {
     		var message = JSON.stringify(controller);
     		
     		
     		if (socket.readyState != 1) {
     			queue.push(message);
     		} else {
         		socket.send(message);
     		}
     	};
     })
	.factory("groundView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
		
		return function (path) {
			var context;
			
			var width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("ground",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.clear = function() {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		    };
			
			chart.draw = function(canvas) {
		        path.context(context);
		        
		        context.drawImage(canvas,0,0);
		    };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("backgroundView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
		
		return function (path) {
			var context;
			
			var width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("background",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.clear = function() {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		    };
			
			chart.draw = function(canvas) {
		        path.context(context);
		        
		        context.drawImage(canvas,0,0);
		    };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("seaView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
		
		return function (path) {
			var context;
			
			var color = "rgba(164,186,199,1.0)",
				width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("sea",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.redraw = function() {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);

		        context.fillStyle = color;
		        context.fillRect(0,0,width,height);
		    };
			
			chart.color = function (value) {
				if (!arguments.length) return color;
				
				color = value;
				
				return chart;
	        };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("landView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
		
		return function (path) {
			var context;
			
			var color = "rgba(215,199,173,1.0)"
				width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("land",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.redraw = function(land) {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		        
		        context.lineWidth = 1.0;
		        context.fillStyle = color;

		        context.beginPath();
		        path(land);
		        context.fill();
		        context.stroke();
		    };
			
			chart.color = function (value) {
				if (!arguments.length) return color;
				
				color = value;
				
				return chart;
	        };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("countriesView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
		
		return function (path) {
			var context;
			
			var color = "rgba(0,0,0,1.0)"
				width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("countries",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.redraw = function (countries) {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		        
		        context.lineWidth = 0.5
		        context.strokeStyle = color;

		        context.beginPath();
		        path(countries);
		        context.stroke();
		    };
			
			chart.color = function (value) {
				if (!arguments.length) return color;
				
				color = value;
				
				return chart;
	        };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("graticuleView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
				
		return function (path) {
			var context;
			
			var graticule = d3.geo.graticule(),
        		color = "rgba(0,0,0,1.0)"
				width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("graticule",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.redraw = function (border) {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		        
		        context.lineWidth = 0.5
		        context.strokeStyle = color;

		        context.beginPath();
		        graticule.lines().forEach(path);
		        context.stroke();
		      
		        context.beginPath();
		        path(graticule.outline());
		        context.stroke();
		    };
			
			chart.color = function (value) {
				if (!arguments.length) return color;
				
				color = value;
				
				return chart;
	        };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("foregroundView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
		
		return function (path) {
			var context;
			
			var width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("foreground",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			};
			
			chart.clear = function() {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		    };
			
			chart.draw = function(canvas) {
		        path.context(context);
		        
		        context.drawImage(canvas,0,0);
		    };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
	.factory("footPrintView", function () {
		var margin = {top: 0, right: 0, bottom: 0, left: 0};
				
		return function (path) {
			var context;
			
			var width = 2000 - margin.left - margin.right,
	        	height = 1000 - margin.top - margin.bottom;
			
			var chart = function (selection) {
		        var canvas = selection.append("canvas")
		        		.classed("footPrint",true)
			            .attr("width", width)
			            .attr("height", height);
		        
			    context = canvas.node().getContext("2d");
			    
			    context.globalAlpha = 0.5;
			};
			
			chart.clear = function() {
		        path.context(context);
		        
		        context.clearRect(0,0,width,height);
		    };
			
			chart.draw = function (foot) {
		        path.context(context);
		                 
		        context.beginPath();
		        path(foot);
		        context.fillStyle = color;
		        context.fill();
		    };
			
			chart.color = function (value) {
				if (!arguments.length) return color;
				
				color = value;
				
				return chart;
	        };
			
			chart.width = function (value) {
				if (!arguments.length) return width;
				
				width = value - margin.top - margin.bottom;
				
				return chart;
	        };
			
			chart.height = function (value) {
				if (!arguments.length) return height;
				
				height = value - margin.top - margin.bottom;
				
				return chart;
	        };
	        
	        return chart;
		};
    })
    .factory("testService", [
    	"assetModelService",
    	"assetControllerService",
    	function (assetModelService,assetControllerService) {
    		var name,seed;
    		
    		name = "Aqua";
			seed = {
				"epoch": { $date: (new Date("2000-01-01T12:00:00Z")).getTime() },
				"a": 7077.7,
				"theta": 0.0,
				"e": 0.0,
				"omega": Math.PI * 90.0 / 180,
				"i": Math.PI * 98.2 / 180,
				"OMEGA": 0.0
			};
			assetModelService( { "name": name, "seed": seed });
			assetControllerService( { "name": name, "seed": seed });
    		
    		name = "Aura";
			seed = {
				"epoch": { $date: (new Date("2000-01-01T12:00:00Z")).getTime() },
				"a": 7077.7,
				"theta": - Math.PI * 45.0 / 180,
				"e": 0.0,
				"omega": Math.PI * 90.0 / 180,
				"i": Math.PI * 98.2 / 180,
				"OMEGA": 0.0
			};
			assetModelService( { "name": name, "seed": seed });
			assetControllerService( { "name": name, "seed": seed });
    		
    		name = "Terra";
			seed = {
				"epoch": { $date: (new Date("2000-01-01T12:00:00Z")).getTime() },
				"a": 7077.7,
				"theta": Math.PI * 45.0 / 180,
				"e": 0.0,
				"omega": Math.PI * 90.0 / 180,
				"i": Math.PI * 98.2 / 180,
				"OMEGA": - Math.PI * 90.0 / 180
			};
			assetModelService( { "name": name, "seed": seed });
			assetControllerService( { "name": name, "seed": seed });
    	}
    ]);