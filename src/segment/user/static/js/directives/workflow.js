

var workflowDirectives = workflowDirectives || angular.module("workflow.directives", [])

workflowDirectives
  .directive("pallete", function factory() {
    return {
      restrict: "E",
      scope: true,
      controller: "PalleteController"
    };
  })
  .directive("editor", function factory() {
    return {
      restrict: "E",
      scope: true,
      controller: "EditorController"
    };
  });
