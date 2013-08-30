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
        routine = routineService(),
        toolbox = toolboxView(),
        editor = editorView();
    
    selection.append("xml").call(toolbox);
    selection.append("div").call(editor);

    routineModel("routine", routine);
    routineModel("toolbox", toolbox.redraw);
    routineModel("editor", editor.redraw);
  }
]);
