var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("toolboxView", [
  function () {
    return function () {
      var groups;
      
      var toolbox = function (selection) {
        var pallete = selection
              .classed("toolbox", true);
        
        var clauses = pallete.append("category").attr("name", "Clauses"),
            routines = pallete.append("category").attr("name", "Routines");
        
        groups = routines.selectAll("category");
        
        clauses.selectAll("category")
            .data(["From", "When", "Given", "Then", "To"])
          .enter().append("block")
            .attr("type", function (d) { return d; });
      };
      
      toolbox.redraw = function (data) {
        data = d3.nest()
          .key(function (d) { return d.type; })
          .entries(data);
      
        groups = groups.data(data);
        
        groups.enter().append("category")
            .attr("name", function (d) { return d.key[0].toUpperCase() + d.key.slice(1) });
        groups.exit().remove();
        
        var blocks = groups.selectAll("block")
          .data(function (d) { return d.values; });
         
        blocks.enter().append("block")
          .attr("type", function (d) { return d.name; });
        blocks.exit().remove();
      };
      
      return toolbox;
    };
  }
]);