var workflowControllers = workflowControllers || angular.module("workflow.controllers", []);

workflowControllers.controller("EditorController", [
  "$scope",
  "$element",
  "editorView",
  function ($scope, $element, editorView) {
    var selection = d3.select($element[0]).append("svg"),
        editor = editorView(),
        story = {
          "name": "Test",
          "nodes": [
          ],
          "links": [
          ],
          "rules": [
          ]
        };
          
    selection.datum(story)
      .call(editor)
      .on("dragover", function () {
        d3.event.preventDefault();
      })
      .on("drop", function () {
        var datum = {
              "_id": d3.event.dataTransfer.getData("oid"),
              "description": ""
            };
        
        story.nodes.push(datum);
        
        editor.redraw();
      });
  }
]);
