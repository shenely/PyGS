var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("outputView", [
  function () {
    return function (values) {
      var self,
          x = 0, y = 0,
          margin = 10;
      
      var group = function (selection) {
        selection.each(function () {
          var group = d3.select(this).append("g")
                .classed("output", true),
              output = group.selectAll("g")
                  .data(values)
                .enter().append("g");
          
          self = group;
                
          output.append("circle")
            .classed("node", true);
            
          output.append("text")
            .classed("h6", true)
            .text(function (d) { return d; })
            .attr("y", -margin)
            .attr("text-anchor", "middle");
            
          var size = 0;
          output.each(function () {
            size = d3.max([size, this.getBBox().width]);
          });
          size *= 1.2;
        
          scale = d3.scale.ordinal()
            .domain(values)
            .rangeBands([- size * values.length / 2, 
                           size * values.length / 2], 0.1);
            
          output.attr("transform", function (d) {
            return "translate(" + (scale(d) + scale.rangeBand() / 2) + ",0)";
          });
            
          group.append("text")
            .classed("h5", true)
            .text("Outputs")
            .attr("x", scale.rangeExtent()[1])
            .attr("y", "-1em")
            .attr("dx", "0.5em")
            .attr("text-anchor", "start");
        });
      };
      
      group.x = function (value) {
        if (!arguments.length) return x;
        
        x = value;
        
        return group;
      };
      
      group.y = function (value) {
        if (!arguments.length) return y;
        
        y = value;
        
        return group;
      };
      
      group.margin = function (value) {
        if (!arguments.length) return margin;
        
        margin = value;
        
        return group;
      };
      
      group.box = function () {
        return self.node().getBBox();
      };
      
      group.rescale = function () { 
        self.attr("transform", "translate(" + x + "," + y + ")");
      };
      
      return group;
    };
  }
]);
