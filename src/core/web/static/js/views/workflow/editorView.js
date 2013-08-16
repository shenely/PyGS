var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("editorView", [
  "objectModel",
  "routineView",
  "nodeView",
  "linkView",
  function (objectModel, routineView,
            nodeView, linkView) {
    return function () {
      var self,
          routines;
      
      var node = nodeView();
          link = linkView();
          
      var drag = d3.behavior.drag()
            .on("drag", function () {
              d3.select(this).
                attr("transform",
                     "translate(" + d3.event.x +
                               "," + d3.event.y + ")");
              
              link.move();
            });
      
      var editor = function (selection) {
        self = selection.classed("editor", true)
          .call(node)
          .call(link);
        
        routines = self.selectAll(".routine");
      };
      
      editor.redraw = function () {
        var story = self.datum();
        
        routines = routines.data(story.nodes);
        routines.enter().append("g")
            .classed("routine", true)
            .each(function (datum, index) {
              var node = objectModel.get(datum._id),
                  routine = routineView()
                    .index(index)
                    .node(node);
              
              d3.select(this).call(routine).call(drag);
            });
        routines.exit().remove();
        
        self.call(node.redraw).call(link.redraw);
      };
      
      return editor;
    };
  }
]);