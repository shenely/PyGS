var workflowControllers = workflowControllers || angular.module("workflow.controllers", []);

workflowControllers.controller("WorkflowController", [
  "$scope",
  "$element",
  "routineService",
  "routineModel",
  "toolboxView",
  "editorView",
  function ($scope, $element, routineService, routineModel, toolboxView, editorView) {
    var selection = d3.select($element[0]),
        toolbox = toolboxView(),
        editor = editorView();
    
    selection.append("xml").call(toolbox);
    selection.append("div").call(editor);

    routineModel("routine", routineService);
    routineModel("toolbox", toolbox.redraw);
    routineModel("editor", editor.redraw);
  }
]);
