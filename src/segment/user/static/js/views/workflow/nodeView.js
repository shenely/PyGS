var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("nodeView", [
  "busService",
  "linkView",
  function (busService, linkView) {
    return function () {
      var origin = d3.select("svg").node().createSVGPoint();
      
      var node = function (selection) {
        selection.selectAll(".node").attr("r", 5);
        
        var link = linkView();
        
        selection.append("g").call(link);
            
        busService.on("done.node", function () {
          var input = selection.selectAll(".input .node"),
              output = selection.selectAll(".output .node"),
              require = selection.selectAll(".require .node"),
              provide = selection.selectAll(".provide .node");
          
          link.draw(selection, output, input);
          link.draw(selection, provide, require);
        });
      };
      
      return node;
    };
  }
]);
