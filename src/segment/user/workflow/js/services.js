angular.module('workflow.services', [])
  .factory("busService", [
    function () {
      return d3.dispatch("done", "link", "drag");
    }
  ])
  .factory("colorService", [
    function () {
      var color = d3.scale.category10()
            .domain(["source", "target", 
                     "condition",
                     "event", "action"]);
                     
      return color;
    }
  ])
  .factory("shapeService", [
    function () {
      return function (points) {
        return function (selection) {
          selection.datum(points)
            .attr("points", function (d) {
              return d.map(function (d) { return d.x + "," + d.y; })
                      .join(" ");
            });
        };
      };
    }
  ])
  .factory("dragService", [
    "busService",
    function (busService) {
      var drag = d3.behavior.drag()
            .origin(Object);
            
      busService.on("drag", function () {
        drag.on("drag", function (d) {
          d3.select(this)
              .attr("transform", "translate(" + (d.x = d.x + d3.event.dx) +
                                          "," + (d.y = d.y + d3.event.dy) + ")");
                                          
          busService.link();
        });
      });
      
      busService.drag();
      
      return drag;
    }
  ])
  .factory("lineService", [
    function () {
      return d3.svg.diagonal();
    }
  ])
  .factory("routineView", [
    "busService",
    "dragService",
    "sourceView",
    "targetView",
    "conditionView",
    "eventView",
    "actionView",
    "requireView",
    "provideView",
    function (busService, dragService,
              sourceView, targetView, 
              conditionView, 
              eventView, actionView, 
              requireView, provideView) {
      var margin = {top: 10, right: 10, bottom: 10, left: 10}
          scale = 40;
      
      return function () {
        var chart = function (enter) {
          enter.append("g").each(function (d) {
            var routine = d3.select(this)
                  .attr("transform","translate(" + (d.x = 800 * Math.random()) +
                                             "," + (d.y = 800 * Math.random()) + ")")
                  .classed("routine", true);
            
            routine.append("rect")
              .attr("x", -margin.left)
              .attr("y", -margin.top)
              .attr("rx", (margin.right + margin.left) / 2)
              .attr("ry", (margin.top + margin.bottom) / 2);
              
            routine.append("text")
              .classed("h4", true)
              .attr("dy", "1em")
              .text(d.name);
            
            switch (d.type) {
              case "source":
                routine.call(sourceView());
                break;
              case "target":
                routine.call(targetView());
                break;
              case "condition":
                routine.call(conditionView());
                break;
              case "event":
                routine.call(eventView());
                break;
              case "action":
                routine.call(actionView());
                break;
            }
              
            routine
              .call(requireView())
               .call(provideView());
              
            var title = routine.select(".h4"),
                process = routine.select(".process"),
                input = routine.select(".input"),
                block = routine.select(".block"),
                output = routine.select(".output"),
                require = routine.select(".require"),
                provide = routine.select(".provide");
                
            var boxes = {
              "title": title.node().getBBox(),
              "require": require.node().getBBox(),
              "provide": provide.node().getBBox(),
              "process": process.node().getBBox(),
              "block": block.node().getBBox(),
              "input": input.node().getBBox(),
              "output": output.node().getBBox()
            };
            
            var width = margin.left
                      + d3.max([boxes.title.width,
                                boxes.require.width])
                      + boxes.process.width
                      + boxes.provide.width
                      + margin.right,
                height = d3.max([margin.top
                                 + boxes.title.height
                                 + d3.max([boxes.require.height,
                                           boxes.provide.height])
                                 + margin.bottom,
                                 boxes.input.height
                                 + boxes.block.height
                                 + boxes.output.height]);
            
            require.attr("transform",
                         "translate(" + (- margin.left) +
                                  "," + boxes.title.height + ")");
            
            process.attr("transform",
                         "translate(" + (d3.max([boxes.title.width,
                                                 boxes.require.width])
                                         + boxes.process.width / 2) +
                                  "," + (height / 2 - margin.top) + ")");
            
            input.attr("transform",
                       "translate(0," + (- height / 2) + ")");
            
            output.attr("transform", 
                        "translate(0," + (height / 2) + ")");
            
            provide.attr("transform", 
                         "translate(" + (margin.left
                                         + d3.max([boxes.title.width,
                                                   boxes.require.width])
                                         + boxes.process.width
                                         + boxes.provide.width) +
                                  "," + boxes.title.height + ")");
            
            routine.select("rect")
              .attr("width", width)
              .attr("height", height);
              
            busService.done();
          }).call(dragService);
        };
      
        return chart;
      };
    }
  ])
  .factory("processView", [
    "blockView",
    "pathView",
    "inputView",
    "outputView",
    function (blockView, pathView,
              inputView, outputView) {
      return function (template, inputs, outputs, paths) {
        var width = 80,
            height = 40;
            
        var process = function (selection) {
          var block = blockView(template)
                .width(width)
                .height(height),
              input = inputView(inputs),
              output = outputView(outputs),
              path = pathView(paths)
                .width(width)
                .height(height);
              
          selection.append("g")
            .classed("process", true)
            .call(path)
            .call(block)
            .call(input)
            .call(output);
        };
        
        return process;
      };
    }
  ])
  .factory("blockView", [
    "colorService",
    "shapeService",
    function (colorService, shapeService) {
      return function (template) {
        var width = 80,
            height = 40;
      
        var block = function (selection) {
          var points = template.map(function (d) {
                return { 
                  "x": width * d.x, 
                  "y": height * d.y 
                };
              }),
              shape = shapeService(points);
              
          selection.append("polygon")
            .classed("block", true)
            .style("fill", function (d) { return colorService(d.type); })
            .call(shape);
        };
        
        block.width = function (value) {
          if (!arguments.length) return width;
          
          width = value;
          
          return block;
        };
        
        block.height = function (value) {
          if (!arguments.length) return height;
          
          height = value;
          
          return block;
        };
        
        return block;
      };
    }
  ])
  .factory("pathView", [
    "busService",
    "lineService",
    function (busService, lineService) {
      return function (paths) {
        var origin = d3.select("svg").node().createSVGPoint();
        
        var width = 80,
            height = 40;
            
        var path = function (selection) {
          var group = selection.append("g");
          
          busService.on("done.path", function () {
            var data = paths.map(function (path) {
                  var source = { 
                        "x": width * path.source.x,
                        "y": height * path.source.y
                      },
                      target = selection.selectAll(".node")
                                .filter(function (d) { 
                                  return d == path.target;
                                }).node();
                    return { "source": source, "target": target };
                }),
                path = group.selectAll(".path")
                    .data(data)
                  .enter().append("path")
                    .classed("path", true);
            
            path.each(function (d) {
              var transform = d.target.getTransformToElement(selection.node());
              
              d.target = origin.matrixTransform(transform);
            });
              
            path.attr("d", lineService);
          });
        };
        
        path.width = function (value) {
          if (!arguments.length) return width;
          
          width = value;
          
          return path;
        };
        
        path.height = function (value) {
          if (!arguments.length) return height;
          
          height = value;
          
          return path;
        };
        
        return path;
      };
    }
  ])
  .factory("nodeView", [
    "busService",
    "dragService",
    "linkView",
    function (busService, dragService, linkView) {
      return function () {
        var origin = d3.select("svg").node().createSVGPoint();
        
        var node = function (selection) {
          var links = [],
              link = linkView(links);
          
          selection.append("g").call(link);
              
          busService.on("done.node", function () {
            var node = selection.selectAll(".node");

            node.on("mousedown", function (d) {
              var mouse = d3.mouse(selection.node());
              
              links.push({ "source": this, "target": null });
              
              busService.link(mouse);
                
              node.on("mouseenter", function (d) {
                  links[links.length-1].target = this;
                  
                  busService.link();
                  
                  selection.on("mousemove", null);
                }).on("mouseleave", function () {
                  links[links.length-1].target = null;
                  
                  selection.on("mousemove", function () {
                    var mouse = d3.mouse(this);
                    
                    busService.link(mouse);
                  });
                });
                
              selection.on("mousemove", function () {
                  var mouse = d3.mouse(this);
                  
                  busService.link(mouse);
                })
                .on("mouseup", function () {
                  node.on("mouseenter",null).on("mouseleave",null);
                  selection.on("mousemove",null).on("mouseup",null);
                  
                  if ((links[links.length-1].source === null) ||
                      (links[links.length-1].target === null)) {
                    links.pop();
                  }
                  
                  busService.link();
                  busService.drag();
                });
                
              dragService.on("drag", null);
            });
          });
        };
        
        return node;
      };
    }
  ])
  .factory("linkView", [
    "busService",
    "lineService",
    function (busService, lineService) {
      return function (links) {
        var origin = d3.select("svg").node().createSVGPoint();
        
        return function (selection) {
          var link = selection.selectAll(".link");
          
          busService.on("link", function (mouse) {
            link = link.data(links);
            
            link.enter().append("path")
              .classed("link", true);
            
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
      };
    }
  ])
  .factory("sourceView", [
    "processView",
    function (processView) {
      var template = [
        { "x": -0.5, "y": -0.5 }, 
        { "x": 0.5, "y": -0.5 }, 
        { "x": 0.5, "y": 0 },
        { "x": 0, "y": 0.5 },
        { "x": -0.5, "y": 0 }
      ];
      
      var inputs = [ ], 
          outputs = [ "out" ],
          paths = [
            { "source": template[3], "target": outputs[0] }
          ];
      
      return function () {
        return processView(template, inputs, outputs, paths);
      };
    }
  ])
  .factory("targetView", [
    "processView",
    function (processView) {
      var template = [
        { "x": -0.5, "y": 0 }, 
        { "x": 0, "y": -0.5 }, 
        { "x": 0.5, "y": 0 },
        { "x": 0.5, "y": 0.5 },
        { "x": -0.5, "y": 0.5 }
      ];
      
      var inputs = [ "in" ], 
          outputs = [ ],
          paths = [
            { "source": template[1], "target": inputs[0] }
          ];
      
      return function () {
        return processView(template, inputs, outputs, paths);
      };
    }
  ])
  .factory("conditionView", [
    "processView",
    function (processView) {
      var template = [
          { "x": -0.5, "y": 0 }, 
          { "x": 0, "y": -0.5 }, 
          { "x": 0.5, "y": 0 },
          { "x": 0, "y": 0.5 }
        ];
      
      var inputs = [ "in" ], 
          outputs = [ "true", "false" ],
          paths = [
            { "source": template[1], "target": inputs[0] },
            { "source": template[0], "target": outputs[0] },
            { "source": template[2], "target": outputs[1] }
          ];
      
      return function () {
        return processView(template, inputs, outputs, paths);
      };
    }
  ])
  .factory("eventView", [
    "processView",
    function (processView) {
      var template = [
          { "x": -0.25, "y": -0.5 },
          { "x": 0.5, "y": -0.5 },
          { "x": 0.25, "y": 0.5 },
          { "x": -0.5, "y": 0.5 }
        ];
      
      var inputs = [ "in" ], 
          outputs = [ "out" ],
          paths = [
            { "source": template[0], "target": inputs[0] },
            { "source": template[2], "target": outputs[0] }
          ];
      
      return function () {
        return processView(template, inputs, outputs, paths);
      };
    }
  ])
  .factory("actionView", [
    "processView",
    function (processView) {
      var template = [
        { "x": -0.5, "y": -0.5 },
        { "x": 0, "y": -0.5 },
        { "x": 0.5, "y": -0.5},
        { "x": 0.5, "y": 0.5 },
        { "x": 0, "y": 0.5 },
        { "x": -0.5, "y": 0.5 }
      ];
      
      var inputs = [ "in" ], 
          outputs = [ "out" ],
          paths = [
            { "source": template[1], "target": inputs[0] },
            { "source": template[4], "target": outputs[0] }
          ];
      
      return function () {
        return processView(template, inputs, outputs, paths);
      };
    }
  ])
  .factory("inputView", [
    function () {
      return function (values) {
        var margin = 10,
            radius = 5;
        
        var group = function (selection) {
          selection.each(function () {
            var group = d3.select(this).append("g")
                  .classed("input", true),
                input = group.selectAll("g")
                    .data(values)
                  .enter().append("g");
                  
            input.append("circle")
              .classed("node", true)
              .attr("r", radius);
              
            input.append("text")
              .classed("h6", true)
              .text(function (d) { return d; })
              .attr("y", margin)
              .attr("dy", "1em")
              .attr("text-anchor", "middle");
              
            var size = 0;
            input.each(function () {
              size = d3.max([size, this.getBBox().width]);
            });
            size *= 1.5;
          
            scale = d3.scale.ordinal()
              .domain(values)
              .rangeBands([- size * values.length / 2, 
                             size * values.length / 2], 0.0);
              
            input.attr("transform", function (d) {
              return "translate(" + (scale(d) + scale.rangeBand() / 2) + ",0)";
            });
              
            group.append("text")
              .classed("h5", true)
              .text("Inputs")
              .attr("x", scale.rangeExtent()[1])
              .attr("y", radius)
              .attr("dx", "0.5em")
              .attr("dy", "1em")
              .attr("text-anchor", "start");
          });
        };
        
        group.radius = function (value) {
          if (!arguments.length) return radius;
          
          radius = value;
          
          return group;
        };
        
        return group;
      };
    }
  ])
  .factory("outputView", [
    function () {
      return function (values) {
        var margin = 10,
            radius = 5;
        
        var group = function (selection) {
          selection.each(function () {
            var group = d3.select(this).append("g")
                  .classed("output", true),
                output = group.selectAll("g")
                    .data(values)
                  .enter().append("g");
                  
            output.append("circle")
              .classed("node", true)
              .attr("r", radius);
              
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
              .attr("y", -radius)
              .attr("dx", "0.5em")
              .attr("text-anchor", "start");
          });
        };
        
        group.radius = function (value) {
          if (!arguments.length) return radius;
          
          radius = value;
          
          return group;
        };
        
        return group;
      };
    }
  ])
  .factory("requireView", [
    function () {
      return function () {
        var margin = 10,
            radius = 5;
            
        var group = function (selection) {
          selection.each(function (d) {
            var group = d3.select(this).append("g")
                  .classed("require", true),
                require = group.selectAll("g")
                    .data(d.properties)
                  .enter().append("g");
              
            var title = group.append("text")
                  .classed("h5", true)
                  .text("Requires")
                  .attr("x", margin)
                  .attr("dy", "1em")
                  .attr("text-anchor", "start")
                offset = title.node().getBBox().height;
                  
            require.append("circle")
              .classed("node", true)
              .attr("r", radius);
              
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
        
        group.radius = function (value) {
          if (!arguments.length) return radius;
          
          radius = value;
          
          return group;
        };
        
        return group;
      };
    }
  ])
  .factory("provideView", [
    function () {
      return function () {
        var margin = 10,
            radius = 5;
            
        var group = function (selection) {
          selection.each(function (d) {
            var group = d3.select(this).append("g")
                  .classed("provide", true),
                provide = group.selectAll("g")
                    .data(d.properties.concat(d.methods.map(function (e) { return e + "()"; })))
                  .enter().append("g");
              
            var title = group.append("text")
                  .classed("h5", true)
                  .text("Provides")
                  .attr("x", -margin)
                  .attr("dy", "1em")
                  .attr("text-anchor", "end"),
                offset = title.node().getBBox().height;
                  
            provide.append("circle")
              .classed("node", true)
              .attr("r", radius);
              
            provide.append("text")
              .classed("h6", true)
              .text(function (d) { return d; })
              .attr("x", -margin)
              .attr("dy", "0.5em")
              .attr("text-anchor", "end");
           
            var size = 0;
            provide.each(function () {
              size = d3.max([size, this.getBBox().height]);
            });
            size *= 1.2;
          
            scale = d3.scale.ordinal()
              .domain(d3.range(d.properties.length + d.methods.length))
              .rangeBands([0, size * (d.properties.length + d.methods.length)], 0.1);
              
            provide.attr("transform", function (d, i) {
              return "translate(0," + (offset
                                       + scale(i)
                                       + scale.rangeBand() / 2) + ")";
            });
          });
        };
        
        group.radius = function (value) {
          if (!arguments.length) return radius;
          
          radius = value;
          
          return group;
        };
        
        return group;
      };
    }
  ]);
