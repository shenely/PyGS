var workflowControllers = workflowControllers || angular.module("workflow.controllers", []);

workflowControllers.controller("EditorController", [
  "$scope",
  "$element",
  "objectModel",
  "editorView",
  function ($scope, $element, objectModel, editorView, routineView, nodeView) {
    var selection = d3.select($element[0]).append("svg"),
        editor = editorView();
    
    var data = [];
          
    selection.call(editor)
      .on("dragover", function () {
        d3.event.preventDefault();
      })
      .on("drop", function () {
        var $oid = d3.event.dataTransfer.getData("oid"),
            datum = objectModel.get($oid);
        
        data.push(datum);
        
        editor.redraw(data)
      });
  }
]);
