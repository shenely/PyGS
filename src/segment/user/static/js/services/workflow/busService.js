var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("busService", [
  function () {
    return d3.dispatch("done", "link", "drag");
  }
]);
