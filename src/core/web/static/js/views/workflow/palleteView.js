var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("toolboxView", [
  function () {
    return function () {
      var groups;
      
      var toolbox = function (selection) {
        var pallete = selection
              .classed("toolbox", true);
        
        var engine = pallete.append("category").attr("name", "Engine"),
            clauses = pallete.append("category").attr("name", "Clauses"),
            routines = pallete.append("category").attr("name", "Routines"),
            statements = pallete.append("category").attr("name", "Statements");
        
        engine.selectAll("block")
            .data(["App", "Story", "Rule"])
          .enter().append("block")
            .attr("type", function (d) { return "engine_" + d; });
        
        clauses.selectAll("block")
            .data(["From", "When", "Given", "Then", "To", "And"])
          .enter().append("block")
            .attr("type", function (d) { return "clause_" + d; });
        
        groups = routines.selectAll("category");
        
        statements.selectAll("block")
            .data(["Routine", "Clause", "Provide", "Require"])
          .enter().append("block")
            .attr("type", function (d) { return "statement_" + d; });
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