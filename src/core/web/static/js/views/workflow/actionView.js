var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("actionView", [
  "processView",
  function (processView) {
    var type = "action",
        template = [
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
      return processView()
        .type(type)
        .template(template)
        .inputs(inputs)
        .outputs(outputs)
        .paths(paths);
    };
  }
]);
