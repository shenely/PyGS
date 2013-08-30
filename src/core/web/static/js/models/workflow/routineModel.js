var workflowModels = workflowModels || angular.module('workflow.models', []);

workflowModels.factory("routineModel", [
  function () {
    var socket = new WebSocket("ws://" + location.host + "/dealer/system/core/engine"),
        dispatch = d3.dispatch("routine");
        data = [];
    
    socket.onopen = function () {
      socket.send("");
    };
    
    socket.onmessage = function (message) {
      var obj = JSON.parse(message.data);
      
      data.push(obj);
      
      dispatch.routine(data);
    };
    
    var routine = function (name, callback) {
      dispatch.on("routine." + name,callback);
    };
    
    routine.get = function (oid) {
      var datum = data.filter(function (d) { return d._id.$oid == oid; })[0];
      
      return datum;
    }
    
    return routine;
  }
]);