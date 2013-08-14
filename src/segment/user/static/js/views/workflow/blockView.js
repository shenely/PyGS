var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("blockView", [
  "colorService",
  "shapeService",
  function (colorService, shapeService) {
    return function (template) {
      var self,
          width = 80,
          height = 40;
    
      var block = function (selection) {
        var points = template.map(function (d) {
              return { 
                "x": width * d.x, 
                "y": height * d.y 
              };
            }),
            shape = shapeService(points);
            
        self = selection.append("polygon")
          .classed("block", true)
          .style("fill", function (d) { return colorService(d.type); })
          .call(shape);
      };
      
      block.width = function (value) {
        if (!arguments.length) return width;
        
        width = value;
        
        return block;
      };
      
      block.height = function (value) {
        if (!arguments.length) return height;
        
        height = value;
        
        return block;
      };
      
      block.box = function () {
        return self.node().getBBox();
      };
      
      block.rescale = function () { };
      
      return block;
    };
  }
]);
