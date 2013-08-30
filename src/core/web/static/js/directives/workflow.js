

var workflowDirectives = workflowDirectives || angular.module("workflow.directives", [])

workflowDirectives
  .directive("workflow", function factory() {
    return {
      restrict: "E",
      scope: true,
      controller: "WorkflowController"
    };
  });
