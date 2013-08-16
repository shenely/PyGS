var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("requireView", [
  function () {
    return function () {
      var x = 0, y = 0,
          margin = 10;
      
      var self,
          index,
          properties, methods;
      
      var require = function (selection) {
        self = selection.append("g")
          .classed("require", true);
        
        var require = self.selectAll("g")
                .data(properties.map(function (property) {
                  return {
                    "index": index,
                    "name": property,
                    "type": "property"
                  };
                }))
              .enter().append("g");
          
        var title = self.append("text")
              .classed("h5", true)
              .text("Requires")
              .attr("x", margin)
              .attr("dy", "1em")
              .attr("text-anchor", "start")
            offset = title.node().getBBox().height;
              
        require.append("circle")
          .classed("node", true);
          
        require.append("text")
          .classed("h6", true)
          .text(function (d) { return d.name; })
          .attr("x", margin)
          .attr("dy", "0.5em");
       
        var size = 0;
        require.each(function () {
          size = d3.max([size, this.getBBox().height]);
        });
        size *= 1.2;
      
        scale = d3.scale.ordinal()
          .domain(d3.range(properties.length + methods.length))
          .rangePoints([0, size * (properties.length + methods.length)], 1.0);
          
        require.attr("transform", function (d, i) {
          return "translate(0," + (offset + scale(i)) + ")";
        });
      };
      
      require.x = function (value) {
        if (!arguments.length) return x;
        
        x = value;
        
        return require;
      };
      
      require.y = function (value) {
        if (!arguments.length) return y;
        
        y = value;
        
        return require;
      };
      
      require.margin = function (value) {
        if (!arguments.length) return margin;
        
        margin = value;
        
        return require;
      };
      
      require.index = function (value) {
        if (!arguments.length) return index;
        
        index = value;
        
        return require;
      };
      
      require.properties = function (value) {
        if (!arguments.length) return properties;
        
        properties = value;
        
        return require;
      };
      
      require.methods = function (value) {
        if (!arguments.length) return methods;
        
        methods = value;
        
        return require;
      };
      
      require.box = function () {
        return self.node().getBBox();
      };
      
      require.rescale = function () { 
        self.attr("transform", "translate(" + x + "," + y + ")");
      };
      
      return require;
    };
  }
]);
