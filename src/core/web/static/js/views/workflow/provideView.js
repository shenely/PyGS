var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("provideView", [
  function () {
    return function () {
      var self,
          x = 0, y = 0,
          margin = 10;
      
      var self,
          index,
          properties, methods;
          
      var provide = function (selection) {
        self = selection.append("g")
          .classed("provide", true);
        
        var provide = self.selectAll("g")
                .data(properties.map(function (property) {
                  return {
                    "index": index,
                    "name": property,
                    "type": "property"
                  };
                })
                .concat(methods.map(function (method) {
                  return {
                    "index": index,
                    "name": method,
                    "type": "method"
                  };
                })))
              .enter().append("g");
            
        var title = self.append("text")
              .classed("h5", true)
              .text("Provides")
              .attr("x", -margin)
              .attr("dy", "1em")
              .attr("text-anchor", "end"),
            offset = title.node().getBBox().height;
              
        provide.append("circle")
          .classed("node", true);
          
        provide.append("text")
          .classed("h6", true)
          .text(function (d) { 
            if (d.type == "property") return d.name;
            else if (d.type == "method") return d.name + "()";
          })
          .attr("x", -margin)
          .attr("dy", "0.5em")
          .attr("text-anchor", "end");
       
        var size = 0;
        provide.each(function () {
          size = d3.max([size, this.getBBox().height]);
        });
        size *= 1.2;
      
        scale = d3.scale.ordinal()
          .domain(d3.range(properties.length + methods.length))
          .rangePoints([0, size * (properties.length + methods.length)], 1.0);
          
        provide.attr("transform", function (d, i) {
          return "translate(0," + (offset + scale(i)) + ")";
        });
      };
      
      provide.x = function (value) {
        if (!arguments.length) return x;
        
        x = value;
        
        return provide;
      };
      
      provide.y = function (value) {
        if (!arguments.length) return y;
        
        y = value;
        
        return provide;
      };
      
      provide.margin = function (value) {
        if (!arguments.length) return margin;
        
        margin = value;
        
        return provide;
      };
      
      provide.index = function (value) {
        if (!arguments.length) return index;
        
        index = value;
        
        return provide;
      };
      
      provide.properties = function (value) {
        if (!arguments.length) return properties;
        
        properties = value;
        
        return provide;
      };
      
      provide.methods = function (value) {
        if (!arguments.length) return methods;
        
        methods = value;
        
        return provide;
      };
      
      provide.box = function () {
        return self.node().getBBox();
      };
      
      provide.rescale = function () { 
        self.attr("transform", "translate(" + x + "," + y + ")");
      };
      
      return provide;
    };
  }
]);
