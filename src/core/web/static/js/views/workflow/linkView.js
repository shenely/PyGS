var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("linkView", [
  function (lineService) {
    return function () {
      var self,
          origin = d3.select("svg").node().createSVGPoint(),
          dispatch = d3.dispatch("start", "move", "end");
          links = [];
          
      var line = d3.svg.diagonal();
          
      dispatch
        .on("start", function (data) {
          d3.event.preventDefault();
          d3.event.stopPropagation();
          
          links.push(data);
          
          self = self.data(links);
          
          self.enter().append("path")
            .classed("link", true);
        })
        .on("move", function (data) {          
          var mouse = d3.mouse(self.node());
          
          if (data !== undefined) {
            links[links.length-1].source = (data.source === undefined) ? links[links.length-1].source : data.source;
            links[links.length-1].target = (data.target === undefined) ? links[links.length-1].target : data.target;
          }
          
          self.attr("d", function (d) {
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
            
            return line({ "source": source, "target": target });
          });
        })
        .on("end", function () {
          d3.event.preventDefault();
          d3.event.stopPropagation();
          
          if ((links[links.length-1].source === null) ||
              (links[links.length-1].target === null)) {
            links.pop();
            
            self = self.data(links);
            
            self.exit().remove();
          }
          
          self
            .on("click", function (d, i) {
              links.splice(i, 1);
              
              self = self.data(links);
              
              self.exit().remove();
              
              dispatch.move();
            })
            .on("mouseenter", function () {
              d3.select(this).classed("active", true);
            })
            .on("mouseleave", function () {
              d3.select(this).classed("active", false);
            });
        });
      
      var link = function (selection) {
        self = selection.append("g").selectAll(".link");
      };
      
      link.redraw = function (selection) {
        var input = selection.selectAll(".input .node"),
            output = selection.selectAll(".output .node"),
            require = selection.selectAll(".require .node"),
            provide = selection.selectAll(".provide .node");
        
        output.on("mousedown", function () {
          dispatch.start({ "source": this, "target": null });
          
          input
            .on("mouseenter", function () {
              dispatch.move({ "target": this });
            })
            .on("mousemove", function () {
              d3.event.stopPropagation();
            })
            .on("mouseleave", function () {
              dispatch.move({ "target": null });
            });
          
          selection
            .on("mousemove", function () {
              dispatch.move({ });
            })
            .on("mouseup", function () {
              dispatch.end();
              
              input.on("mouseenter", null).on("mouseleave", null).on("mousemove", null);
              selection.on("mousemove", null).on("mouseup", null);
            });
        });
        
        input.on("mousedown", function () {
          dispatch.start({ "source": null, "target": this });
          
          output
            .on("mouseenter", function () {
              dispatch.move({ "source": this });
            })
            .on("mousemove", function () {
              d3.event.stopPropagation();
            })
            .on("mouseleave", function () {
              dispatch.move({ "source": null });
            });
          
          selection
            .on("mousemove", function () {
              dispatch.move({ });
            })
            .on("mouseup", function () {
              dispatch.end();
              
              output.on("mouseenter", null).on("mouseleave", null).on("mousemove", null);
              selection.on("mousemove", null).on("mouseup", null);
            });
        });
        
        provide.on("mousedown", function () {
          dispatch.start({ "source": this, "target": null });
          
          require
            .on("mouseenter", function () {
              dispatch.move({ "target": this });
            })
            .on("mousemove", function () {
              d3.event.stopPropagation();
            })
            .on("mouseleave", function () {
              dispatch.move({ "target": null });
            });
          
          selection
            .on("mousemove", function () {
              dispatch.move({ });
            })
            .on("mouseup", function () {
              dispatch.end();
              
              require.on("mouseenter", null).on("mouseleave", null).on("mousemove", null);
              selection.on("mousemove", null).on("mouseup", null);
            });
        });
        
        require.on("mousedown", function () {
          dispatch.start({ "source": null, "target": this });
          
          provide
            .on("mouseenter", function () {
              dispatch.move({ "source": this });
            })
            .on("mousemove", function () {
              d3.event.stopPropagation();
            })
            .on("mouseleave", function () {
              dispatch.move({ "source": null });
            });
          
          selection
            .on("mousemove", function () {
              dispatch.move({ });
            })
            .on("mouseup", function () {
              dispatch.end();
              
              provide.on("mouseenter", null).on("mouseleave", null).on("mousemove", null);
              selection.on("mousemove", null).on("mouseup", null);
            });
        });
      };
      
      link.start = function (name, callback) {
        dispatch.start();
      };
      
      link.move = function (name, callback) {
        dispatch.move();
      };
      
      link.end = function () {
        dispatch.end();
      };
      
      return link;
    };
  }
]);
