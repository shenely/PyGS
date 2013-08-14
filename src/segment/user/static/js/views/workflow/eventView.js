var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("eventView", [
  "processView",
  function (processView) {
    var name = "event",
        template = [
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
      return processView()
        .classed(name)
        .template(template)
        .inputs(inputs)
        .outputs(outputs)
        .paths(paths);
    };
  }
]);
