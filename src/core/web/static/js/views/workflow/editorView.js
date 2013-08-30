var workflowViews = workflowViews || angular.module('workflow.views', []);

workflowViews.factory("editorView", [
  function () {
    return function () {
      var self, timer;
      
      var editor = function (selection) {
        self = selection.classed("editor", true);
        
        timer = setTimeout(function () {
          var toolbox = d3.select(".toolbox");
          
          Blockly.inject(self.node(),
              { 
                path: './', toolbox: toolbox.node(),
                trashcan: false
              });
        }, 500);
      };
      
      editor.redraw = function () {
        clearTimeout(timer);
        
        timer = setTimeout(function () {
          var toolbox = d3.select(".toolbox");
          
          Blockly.inject(self.node(),
              { 
                path: './',
                toolbox: toolbox.node(),
                trashcan: false
              });
        }, 500);
      };
      
      return editor;
    };
  }
]);