var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("generalView", [
  "processView",
  function (processView) {
    var name = "general",
        template = [
          { "x": -0.5, "y": -0.5 }, 
          { "x": 0.5, "y": 0 }, 
          { "x": -0.5, "y": 0.5 }
        ];
    
    var inputs = [ ], 
        outputs = [ ],
        paths = [ ];
    
    return function () {
      return processView()
        .classed(name)
        .template(template)
        .inputs(inputs)
        .outputs(outputs)
        .paths(paths);
    };
  }
]);
