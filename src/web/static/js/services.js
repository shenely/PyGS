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
	.factory("test", function () {
		var name = "Aqua",
			state = {
				"epoch": { $date: (new Date("2000-01-01T12:00:00Z")).getTime() },
				"a": 10000.0,
				"theta": 0.0,
				"e": 0.2,
				"omega": Math.PI * 90.0 / 180,
				"i": Math.PI * 60.0 / 180,
				"OMEGA": 0.0
			};
		
		var model = new WebSocket("ws://" + location.host + "/pub/system/asset/model");
		model.onopen = function () {
			model.send(JSON.stringify({
				"name": name,
				"seed": state
			}));
			
			model.close();
		};
		
		var controller = new WebSocket("ws://" + location.host + "/pub/system/asset/controller");
		controller.onopen = function () {
			controller.send(JSON.stringify({
				"name": name,
				"seed": state
			}));
			
			controller.close();
		};
		
		var view = new WebSocket("ws://" + location.host + "/pub/system/asset/view");
		view.onopen = function () {
			view.send(JSON.stringify({
				"name": name
			}));
			
			view.close();
		};
		
		return true;
	})
	.factory("inertial", function() {
		var socket = new WebSocket("ws://" + location.host + "/sub/aqua/user/inertial"),
			epoch = [],
			state = [];
		
		var view = null;
		socket.onmessage = function(event) {
			view = JSON.parse(event.data);
			
			epoch.forEach(function(callback) { return callback(view.epoch.$date); });
			state.forEach(function(callback) { return callback(view); });
		};
		
		return {
			epoch: function(callback) { epoch.push(callback) },
			state: function(callback) { state.push(callback); }
		};
	})
	.factory("geographic", function() {		
		var socket = new WebSocket("ws://" + location.host + "/sub/aqua/user/geographic"),
			epoch = [],
			state = [];
		
		var view = null;
		socket.onmessage = function(event) {
			view = JSON.parse(event.data);
			
			epoch.forEach(function(callback) { return callback(view.epoch.$date); });
			state.forEach(function(callback) { return callback(view); });
		};
		
		return {
			epoch: function(callback) { epoch.push(callback) },
			state: function(callback) { state.push(callback); }
		};
	});