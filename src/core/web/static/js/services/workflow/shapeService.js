var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("shapeService", [
  function () {
    return function (points) {
      return function (selection) {
        selection.datum(points)
          .attr("points", function (d) {
            return d.map(function (d) { return d.x + "," + d.y; })
                    .join(" ");
          });
      };
    };
  }
]);
