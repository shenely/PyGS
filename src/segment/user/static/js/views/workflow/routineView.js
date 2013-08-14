var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("routineView", [
  "sourceView",
  "targetView",
  "conditionView",
  "eventView",
  "actionView",
  "generalView",
  "specialView",
  "requireView",
  "provideView",
  "nodeView",
  function (sourceView, targetView, 
            conditionView, 
            eventView, actionView, 
            generalView, specialView,
            requireView, provideView,
            nodeView) {
    var self,
        margin = {top: 10, right: 10, bottom: 10, left: 10},
        width, height,
        scale = 40;
    
    var title, process, require, provide;
    
    return function () {
      var routine = function (routine) {
        var datum = routine.datum(),
            mouse = d3.mouse(routine.node().parentNode);
        
        routine.attr("transform",
                     "translate(" + mouse[0] +
                              "," + mouse[1] + ")");
                  
        self = routine.append("rect")
          .attr("x", -margin.left)
          .attr("y", -margin.top)
          .attr("rx", (margin.right + margin.left) / 2)
          .attr("ry", (margin.top + margin.bottom) / 2);
          
        title = routine.append("text")
          .classed("h4", true)
          .attr("dy", "1em")
          .text(datum.name);
        
        switch (datum.type) {
          case "source":
            process = sourceView();
            break;
          case "target":
            process = targetView();
            break;
          case "condition":
            process = conditionView();
            break;
          case "event":
            process = eventView();
            break;
          case "action":
            process = actionView();
            break;
          case "general":
            process = generalView();
            break;
          case "special":
            process = specialView();
            break;
        }
        
        require = requireView();
        provide = provideView();
        
        var node = nodeView();
          
        routine
          .call(process)
          .call(require)
          .call(provide)
          .call(node);
      };
      
      routine.rescale =  function () {
        var boxes = {
            "title": title.node().getBBox(),
            "require": require.box(),
            "provide": provide.box(),
            "process": process.box(),
            "block": process.block().box(),
            "input": process.input().box(),
            "output": process.output().box()
          };
          
        width = margin.left
                + d3.max([boxes.title.width,
                          boxes.require.width])
                + boxes.process.width
                + boxes.provide.width
                + margin.right;
        height = d3.max([margin.top
                         + boxes.title.height
                         + d3.max([boxes.require.height,
                                   boxes.provide.height])
                         + margin.bottom,
                         boxes.input.height
                         + boxes.block.height
                         + boxes.output.height]);
        
        require
          .x(- margin.left)
          .y(boxes.title.height);
        
        process
          .x(d3.max([boxes.title.width,
                     boxes.require.width])
             + boxes.process.width / 2)
          .y(height / 2 - margin.top);
        
        process.input()
          .x(0)
          .y(- height / 2);
        
        process.output()
          .x(0)
          .y(height / 2);
        
        provide
          .x(margin.left
             + d3.max([boxes.title.width,
                       boxes.require.width])
             + boxes.process.width
             + boxes.provide.width)
          .y(boxes.title.height);
        
        self.attr("width", width).attr("height", height);
        
        process.rescale();
        require.rescale();
        provide.rescale();
      };
    
      return routine;
    };
  }
]);
