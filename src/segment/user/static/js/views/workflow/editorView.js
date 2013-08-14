var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("editorView", [
  "routineView",
  function (routineView) {
    return function () {
      var routine = routineView(),
          editor, routines;
      
      var editor = function (selection) {
        editor = selection.classed("editor", true);
  
        routines = editor.selectAll(".routine");
      };
      
      editor.redraw = function (data) {
        routines = routines.data(data);
        
        routines.enter().append("g").classed("routine", true)
          .each(function () {
            var routine = routineView();
            
            d3.select(this).call(routine);
            
            routine.rescale();
          });
        routines.exit().remove();
      };
      
      return editor;
    };
  }
]);