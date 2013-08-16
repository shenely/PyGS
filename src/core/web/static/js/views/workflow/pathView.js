var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("pathView", [
  function () {
    var line = d3.svg.diagonal();
    
    return function (paths) {
      var origin = d3.select("svg").node().createSVGPoint();
      
      var width = 80,
          height = 40;
          
      var path = function (selection) {
        selection.selectAll().remove();
        
        var group = selection.insert("g", ".block"),
            data = paths.map(function (path) {
                var source = { 
                      "x": width * path.source.x,
                      "y": height * path.source.y
                    },
                    target = selection.selectAll(".node")
                              .filter(function (d) { 
                                return d.name == path.target;
                              }).node();
                  return { "source": source, "target": target };
              }),
              path = group.selectAll(".path")
                  .data(data)
                .enter().append("path")
                  .classed("path", true);
          
        path.each(function (d) {
          var transform = d.target.getTransformToElement(this);
          
          d.target = origin.matrixTransform(transform);
        });
          
        path.attr("d", line);
      };
      
      path.width = function (value) {
        if (!arguments.length) return width;
        
        width = value;
        
        return path;
      };
      
      path.height = function (value) {
        if (!arguments.length) return height;
        
        height = value;
        
        return path;
      };
      
      return path;
    };
  }
])
