var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("colorService", [
  function () {
    var color = d3.scale.category10()
          .domain(["source", "target", 
                   "condition",
                   "event", "action"]);
                   
    return function (d) { return d3.lab(color(d)); };
  }
]);
