var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("outputView", [
  function () {
    return function (values) {
      var self,
          x = 0, y = 0,
          margin = 10;
      
      var index, type;
      
      var self;
      
      var output = function (selection) {
        self = selection.append("g")
          .classed("output", true);
          
        var output = self.selectAll("g")
                .data(values.map(function (d) {
                  return {
                    "index": index,
                    "name": d,
                    "type": type                   
                  };
                }))
              .enter().append("g");
              
        output.append("circle")
          .classed("node", true);
          
        output.append("text")
          .classed("h6", true)
          .text(function (d) { return d.name; })
          .attr("y", -margin)
          .attr("text-anchor", "middle");
          
        var size = 0;
        output.each(function () {
          size = d3.max([size, this.getBBox().width]);
        });
        size *= 1.2;
      
        scale = d3.scale.ordinal()
          .domain(values)
          .rangePoints([- size * values.length / 2, 
                         size * values.length / 2], 1.0);
          
        output.attr("transform", function (d) {
          return "translate(" + scale(d.name) + ",0)";
        });
          
        self.append("text")
          .classed("h5", true)
          .text("Outputs")
          .attr("x", scale.rangeExtent()[1])
          .attr("y", -margin/2)
          .attr("dx", "0.5em")
          .attr("text-anchor", "start");
      };
      
      output.x = function (value) {
        if (!arguments.length) return x;
        
        x = value;
        
        return output;
      };
      
      output.y = function (value) {
        if (!arguments.length) return y;
        
        y = value;
        
        return output;
      };
      
      output.margin = function (value) {
        if (!arguments.length) return margin;
        
        margin = value;
        
        return output;
      };
      
      output.index = function (value) {
        if (!arguments.length) return index;
        
        index = value;
        
        return output;
      };
      
      output.type = function (value) {
        if (!arguments.length) return type;
        
        type = value;
        
        return output;
      };
      
      output.box = function () {
        return self.node().getBBox();
      };
      
      output.rescale = function () { 
        self.attr("transform", "translate(" + x + "," + y + ")");
      };
      
      return output;
    };
  }
]);
