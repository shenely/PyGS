'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('kepler.services', [])
	.factory("cartograph", function() {
		return function(width, height) {
			var width = 1000,
			    height = 500;
			
			var projection = d3.geo.equirectangular()
			    .translate([ width / 2, height / 2])
			    .scale(height / Math.PI);
			
			return d3.geo.path().projection(projection);;
		};
	})
	.factory("world", ["$http", function($http) {
		return $http.get("/static/dat/world-110m.json");
	}])
	.factory("global2d", function() {		
		var socket = new WebSocket("ws://" + location.host + "/view/global2"),
			epoch = [],
			states = [];
		
		var view = null;
		socket.onmessage = function(event) {
			view = JSON.parse(event.data).params;
			
			epoch.forEach(function(callback) { return callback(view.epoch.$date); });
			states.forEach(function(callback) { return callback(view.states); });
		};
		
		return {
			epoch: function(callback) { epoch.push(callback) },
			states: function(callback) { states.push(callback); }
		};
	});