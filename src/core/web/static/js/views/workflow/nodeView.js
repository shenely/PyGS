var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("nodeView", [
  "linkView",
  function (linkView) {
    return function () {
      var self,
          radius = 5;
      
      var node = function (selection) {
      };
      
      node.radius = function (value) {
        if (!arguments.length) return radius;
        
        radius = value;
        
        return node;
      };
      
      node.rescale = function () {
        self.attr("r", radius);
      };
      
      node.redraw = function (selection) {
        selection.selectAll(".node").attr("r", radius);
      };
      
      return node;
    };
  }
]);
