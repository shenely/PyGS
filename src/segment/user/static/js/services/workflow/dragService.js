var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("dragService", [
  "busService",
  function (busService) {
    var drag = d3.behavior.drag()
          .origin(Object);
          
    busService.on("drag", function () {
      drag.on("drag", function (d) {
        d3.select(this)
            .attr("transform", "translate(" + (d.x = d.x + d3.event.dx) +
                                        "," + (d.y = d.y + d3.event.dy) + ")");
                                        
        busService.link();
      });
    });
    
    busService.drag();
    
    return drag;
  }
]);
