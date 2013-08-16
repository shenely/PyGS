var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("sourceView", [
  "processView",
  function (processView) {
    var type = "source",
        template = [
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
      return processView()
        .type(type)
        .template(template)
        .inputs(inputs)
        .outputs(outputs)
        .paths(paths);
    };
  }
]);
