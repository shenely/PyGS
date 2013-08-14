var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("requireView", [
  function () {
    return function () {
      var self,
          x = 0, y = 0,
          margin = 10;
          
      var group = function (selection) {
        selection.each(function (d) {
          var group = d3.select(this).append("g")
                .classed("require", true),
              require = group.selectAll("g")
                  .data(d.properties)
                .enter().append("g");
          
          self = group;
            
          var title = group.append("text")
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
            .text(function (d) { return d; })
            .attr("x", margin)
            .attr("dy", "0.5em");
         
          var size = 0;
          require.each(function () {
            size = d3.max([size, this.getBBox().height]);
          });
          size *= 1.2;
        
          scale = d3.scale.ordinal()
            .domain(d3.range(d.properties.length + d.methods.length))
            .rangeBands([0, size * (d.properties.length + d.methods.length)], 0.1);
            
          require.attr("transform", function (d, i) {
            return "translate(0," + (offset
                                     + scale(i)
                                     + scale.rangeBand() / 2) + ")";
          });       
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
