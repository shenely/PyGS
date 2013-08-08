angular.module("workflow.directives", [])
  .directive("workflow", function factory() {
    return {
      restrict: "E",
      scope: true,
      controller: "WorkflowController"
    };
  });
