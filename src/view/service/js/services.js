'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('kepler.services', [])
	.factory("cartograph", function() {
		return function(width, height) {			
			var projection = d3.geo.equirectangular()
			    .translate([ width / 2, height / 2])
			    .scale(height / Math.PI);
			
			return d3.geo.path().projection(projection);
		};
	})
	.factory("world", ["$http", function($http) {
		return $http.get("/static/dat/world-110m.json");
	}])
	.factory("inertial", function() {		
		var socket = new WebSocket("ws://" + location.host + "/notice/inertial"),
			epoch = [],
			assets = [];
		
		var view = null;
		socket.onmessage = function(event) {
			view = JSON.parse(event.data);
			
			epoch.forEach(function(callback) { return callback(view.epoch.$date); });
			assets.forEach(function(callback) { return callback(view.assets); });
		};
		
		return {
			epoch: function(callback) { epoch.push(callback) },
			assets: function(callback) { assets.push(callback); }
		};
	})
	.factory("geographic", function() {		
		var socket = new WebSocket("ws://" + location.host + "/notice/geographic"),
			epoch = [],
			assets = [];
		
		var view = null;
		socket.onmessage = function(event) {
			view = JSON.parse(event.data);
			
			epoch.forEach(function(callback) { return callback(view.epoch.$date); });
			assets.forEach(function(callback) { return callback(view.assets); });
		};
		
		return {
			epoch: function(callback) { epoch.push(callback) },
			assets: function(callback) { assets.push(callback); }
		};
	});