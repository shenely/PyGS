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
  function (sourceView, targetView, 
            conditionView, 
            eventView, actionView, 
            generalView, specialView,
            requireView, provideView) {    
    return function () {
      var margin = {top: 10, right: 10, bottom: 10, left: 10},
          width, height;
      
      var index, node;
      
      var routine = function (selection) {
        var mouse = d3.mouse(selection.node());
        
        selection.attr("transform",
                       "translate(" + mouse[0] +
                                "," + mouse[1] + ")");
                  
        var self = selection.append("rect")
              .attr("x", -margin.left)
              .attr("y", -margin.top)
              .attr("rx", (margin.right + margin.left) / 2)
              .attr("ry", (margin.top + margin.bottom) / 2);
        
        var title = selection.append("text")
              .classed("h4", true)
              .attr("dy", "1em")
              .text(node.name);
      
        switch (node.type) {
          case "source":
            var process = sourceView().index(index);
            break;
          case "target":
            var process = targetView().index(index);
            break;
          case "condition":
            var process = conditionView().index(index);
            break;
          case "event":
            var process = eventView().index(index);
            break;
          case "action":
            var process = actionView().index(index);
            break;
          case "general":
            var process = generalView().index(index);
            break;
          case "special":
            var process = specialView().index(index);
            break;
        }
        
        var require = requireView()
              .index(index)
              .properties(node.properties)
              .methods(node.methods),
            provide = provideView()
              .index(index)
              .properties(node.properties)
              .methods(node.methods);
          
        selection
          .call(process)
          .call(require)
          .call(provide);
        
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
          
        height = d3.max([
                         margin.top
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
      
      routine.index = function (value) {
        if (!arguments.length) return index;
        
        index = value;
        
        return routine;
      };
      
      routine.node = function (value) {
        if (!arguments.length) return node;
        
        node = value;
        
        return routine;
      };
      
      return routine;
    };
  }
]);