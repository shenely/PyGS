var workflowControllers = workflowControllers || angular.module("workflow.controllers", []);

workflowControllers.controller("PalleteController", [
  "$scope",
  "$element",
  "objectModel",
  "palleteView",
  function ($scope, $element, objectModel, palleteView) {
    var selection = d3.select($element[0]).append("div"),
        pallete = palleteView();
    
    selection.call(pallete);
    
    objectModel("pallete", pallete.redraw);
  }
]);
