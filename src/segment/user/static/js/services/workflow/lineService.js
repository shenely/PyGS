var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("lineService", [
  function () {
    return d3.svg.diagonal();
  }
]);
