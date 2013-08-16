var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("targetView", [
  "processView",
  function (processView) {
    var type = "target",
        template = [
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
      return processView()
        .type(type)
        .template(template)
        .inputs(inputs)
        .outputs(outputs)
        .paths(paths);
    };
  }
]);
