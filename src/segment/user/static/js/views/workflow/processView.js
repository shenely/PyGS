var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("processView", [
  "blockView",
  "pathView",
  "inputView",
  "outputView",
  function (blockView, pathView,
            inputView, outputView) {
    return function () {
      var self,
          x = 0, y = 0,
          width = 80,
          height = 40,
          margin = 10,
          classed = "default",
          template = [],
          inputs = [],
          outputs = []
          paths = [];
      
      var block, path,
          input, output;
          
      var process = function (selection) {
        block = blockView(template)
          .width(width)
          .height(height);
        path = pathView(paths)
          .width(width)
          .height(height);
        input = inputView(inputs)
          .margin(margin);
        output = outputView(outputs)
          .margin(margin);
            
        self = selection.append("g")
          .classed("process " + classed, true)
          .call(block)
          .call(input)
          .call(output);
      };
      
      process.x = function (value) {
        if (!arguments.length) return x;
        
        x = value;
        
        return process;
      };
      
      process.y = function (value) {
        if (!arguments.length) return y;
        
        y = value;
        
        return process;
      };
      
      process.classed = function (value) {
        if (!arguments.length) return classed;
        
        classed = value;
        
        return process;
      };
      
      process.template = function (value) {
        if (!arguments.length) return template;
        
        template = value;
        
        return process;
      };
      
      process.inputs = function (value) {
        if (!arguments.length) return inputs;
        
        inputs = value;
        
        return process;
      };
      
      process.outputs = function (value) {
        if (!arguments.length) return outputs;
        
        outputs = value;
        
        return process;
      };
      
      process.paths = function (value) {
        if (!arguments.length) return paths;
        
        paths = value;
        
        return process;
      };
      
      process.block = function () {
        return block;
      };
      
      process.path = function () {
        return path;
      };
      
      process.input = function () {
        return input;
      };
      
      process.output = function () {
        return output;
      };
      
      process.box = function () {
        return self.node().getBBox();
      };
      
      process.rescale = function () {
        self.attr("transform", "translate(" + x + "," + y + ")");
        
        block.rescale();
        input.rescale();
        output.rescale();
        
        self.call(path)
      };
      
      return process;
    };
  }
])
