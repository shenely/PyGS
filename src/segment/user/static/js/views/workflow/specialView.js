var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("specialView", [
  "processView",
  function (processView) {
    var name = "special",
        template = [
          { "x": 0, "y": 0 }
        ];
    
    var inputs = [ "in" ], 
        outputs = [ "out" ],
        paths = [
          { "source": template[0], "target": inputs[0] },
          { "source": template[0], "target": outputs[0] }
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
