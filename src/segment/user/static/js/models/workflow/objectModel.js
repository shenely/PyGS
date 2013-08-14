var workflowModels = workflowModels || angular.module('workflow.models', []);

workflowModels.factory("objectModel", [
  function () {
    var socket = new WebSocket("ws://" + location.host + "/dealer/system/core/engine"),
        dispatch = d3.dispatch("object");
        data = [];
    
    socket.onopen = function () {
      socket.send("");
    };
    
    socket.onmessage = function (message) {
      var obj = JSON.parse(message.data);
      
      data.push(obj);
      
      dispatch.object(data);
    };
    
    var object = function (name, callback) {
      dispatch.on("object." + name,callback);
    };
    
    object.get = function (oid) {
      var datum = data.filter(function (d) { return d._id.$oid == oid; })[0];
      
      return datum;
    }
    
    return object;
  }
]);