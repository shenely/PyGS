var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("palleteView", [
  "colorService",
  function (colorService) {
    return function () {
      var groups,items;
      
      var pallete = function (selection) {
        var pallete = selection
              .classed("pallete", true)
              .append("ul");
        
        groups = pallete.selectAll(".group");
      };
      
      pallete.redraw = function (data) {
        data = d3.nest()
          .key(function (d) { return d.type; })
          .entries(data);
      
        groups = groups.data(data);
        
        var enter = groups.enter().append("li") .classed("group", true);
        enter.append("div");
        enter.append("ul");
        
        groups.selectAll("div")
          .text(function (d) { return d.key; })
          .style("background-color", function (d) { return colorService(d.key).brighter(); });
        
        groups.exit().remove();
        
        items = groups.select("ul").selectAll(".item")
              .data(function (d) { return d.values; });
         
        items.enter().append("li").classed("item", true)
          .attr("draggable", true)
          .on("dragstart", function (d) {
            d3.event.dataTransfer.setData("oid", d._id.$oid);
          });
        items.text(function (d) { return d.name; });
        items.exit().remove();
      };
      
      return pallete;
    };
  }
]);