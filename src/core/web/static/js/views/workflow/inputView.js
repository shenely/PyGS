var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("inputView", [
  function () {
    return function (values) {
      var self,
          x = 0, y = 0,
          margin = 10;
      
      var index, type;
      
      var self;
      
      var input = function (selection) {
        self = selection.append("g")
              .classed("input", true);
              
        var input = self.selectAll("g")
                .data(values.map(function (d) {
                  return {
                    "index": index,
                    "name": d,
                    "type": type                   
                  };
                }))
              .enter().append("g");
                
        input.append("circle")
          .classed("node", true);
          
        input.append("text")
          .classed("h6", true)
          .text(function (d) { return d.name; })
          .attr("y", margin)
          .attr("dy", "1em")
          .attr("text-anchor", "middle");
          
        var size = 0;
        input.each(function () {
          size = d3.max([size, this.getBBox().width]);
        });
        size *= 1.2;
      
        scale = d3.scale.ordinal()
          .domain(values)
          .rangePoints([- size * values.length / 2, 
                         size * values.length / 2], 1.0);
          
        input.attr("transform", function (d) {
          return "translate(" + scale(d.name) + ",0)";
        });
          
        self.append("text")
          .classed("h5", true)
          .text("Inputs")
          .attr("x", scale.rangeExtent()[1])
          .attr("y", margin/2)
          .attr("dx", "0.5em")
          .attr("dy", "1em")
          .attr("text-anchor", "start");
      };
      
      input.x = function (value) {
        if (!arguments.length) return x;
        
        x = value;
        
        return input;
      };
      
      input.y = function (value) {
        if (!arguments.length) return y;
        
        y = value;
        
        return input;
      };
      
      input.margin = function (value) {
        if (!arguments.length) return margin;
        
        margin = value;
        
        return input;
      };
      
      input.index = function (value) {
        if (!arguments.length) return index;
        
        index = value;
        
        return input;
      };
      
      input.type = function (value) {
        if (!arguments.length) return type;
        
        type = value;
        
        return input;
      };
      
      input.box = function () {
        return self.node().getBBox();
      };
      
      input.rescale = function () { 
        self.attr("transform", "translate(" + x + "," + y + ")");
      };
      
      return input;
    };
  }
]);
