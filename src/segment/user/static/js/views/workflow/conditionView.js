var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("conditionView", [
  "processView",
  function (processView) {
    var name = "condition",
        template = [
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
      return processView()
        .classed(name)
        .template(template)
        .inputs(inputs)
        .outputs(outputs)
        .paths(paths);
    };
  }
]);
