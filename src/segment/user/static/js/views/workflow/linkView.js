var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("linkView", [
  "busService",
  "dragService",
  "lineService",
  function (busService, dragService, lineService) {
    return function () {
      var origin = d3.select("svg").node().createSVGPoint(),
          links = [];
      
      var link = function (selection) {
        var link = selection.selectAll(".link");
        
        busService.on("link", function (mouse) {
          link = link.data(links);
          
          link.enter().append("path")
            .classed("link", true)
            .on("mouseover", function () {
              d3.select(this).classed("active", true);
            })
            .on("mouseout", function () {
              d3.select(this).classed("active", false);
            })
            .on("click", function (d, i) {
              links.splice(i, 1);
              
              busService.link();
            });
          
          link.attr("d", function (d) {
            if (d.source !== null) {
              var transform = d.source.getCTM(),
                  source = origin.matrixTransform(transform);
            } else {
              var source = { "x": mouse[0], "y": mouse[1] };
            }
            
            if (d.target !== null) {
              var transform = d.target.getCTM(),
                  target = origin.matrixTransform(transform);
            } else {
              var target = { "x": mouse[0], "y": mouse[1] };
            }
            
            return lineService({ "source": source, "target": target });
          });
          
          link.exit().remove();
        });
      };
      
      link.draw = function (selection, source, target) {
        source
          .on("mousedown", function (d) {
            var mouse = d3.mouse(selection.node()),
                node = d3.select(this);
            
            links.push({ "source": this, "handle": null, "target": null });
            
            node.classed("active", true);
            target.classed("active", true);
            
            busService.link(mouse);
              
            target
              .on("mouseenter", function (d) {
                links[links.length-1].target = this;
                
                busService.link();
                
                selection.on("mousemove", null);
              })
              .on("mouseleave", function () {
                links[links.length-1].target = null;
                
                selection.on("mousemove", function () {
                  var mouse = d3.mouse(this);
                  
                  busService.link(mouse);
                });
              });
              
            selection
              .on("mousemove", function () {
                var mouse = d3.mouse(this);
                
                busService.link(mouse);
              })
              .on("mouseup", function () {
                target.on("mouseenter",null).on("mouseleave",null);
                selection.on("mousemove",null).on("mouseup",null);
                
                if ((links[links.length-1].source === null) ||
                    (links[links.length-1].target === null)) {
                  links.pop();
                } else {
                  links[links.length-1].handle = {
                    "x": (links[links.length-1].source.x
                        + links[links.length-1].target.x) / 2,
                    "y": (links[links.length-1].source.y
                        + links[links.length-1].target.y) / 2
                  };
                }
            
                node.classed("active", false);
                target.classed("active", false);
                
                busService.link();
                busService.drag();
              });
              
            dragService.on("drag", null);
          });
            
        target
          .on("mousedown", function (d) {
            var mouse = d3.mouse(selection.node()),
                node = d3.select(this);
            
            links.push({ "source": null, "target": this });
            
            node.classed("active", true);
            source.classed("active", true);
            
            busService.link(mouse);
              
            source
              .on("mouseenter", function (d) {
                links[links.length-1].source = this;
                
                busService.link();
                
                selection.on("mousemove", null);
              })
              .on("mouseleave", function () {
                links[links.length-1].source = null;
                
                selection.on("mousemove", function () {
                  var mouse = d3.mouse(this);
                  
                  busService.link(mouse);
                });
              });
              
            selection
              .on("mousemove", function () {
                var mouse = d3.mouse(this);
                
                busService.link(mouse);
              })
              .on("mouseup", function () {
                source.on("mouseenter",null).on("mouseleave",null);
                selection.on("mousemove",null).on("mouseup",null);
                
                if ((links[links.length-1].source === null) ||
                    (links[links.length-1].target === null)) {
                  links.pop();
                } else {
                  links[links.length-1].handle = {
                    "x": (links[links.length-1].source.x
                        + links[links.length-1].target.x) / 2,
                    "y": (links[links.length-1].source.y
                        + links[links.length-1].target.y) / 2
                  };
                }
            
                node.classed("active", false);
                source.classed("active", false);
                
                busService.link();
                busService.drag();
              });
              
            dragService.on("drag", null);
          });
      };
      
      return link;
    };
  }
]);
