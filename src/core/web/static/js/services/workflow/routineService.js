var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("routineService", [
  function () {
    return function () {      
      var routine = function (data) {
        var datum = data[data.length-1];
        
        Blockly.Language[datum.name] = {
            category: datum.type,
            init: function() {
              this.setColour(65);
              this.appendDummyInput()
                  .appendTitle(datum.name)
                  .appendTitle(datum.type + ":");
              this.appendDummyInput()
                  .appendTitle(new Blockly.FieldTextInput("description"), "description");
              this.appendStatementInput("sat");
              this.appendValueInput("socket")
                  .setAlign(Blockly.ALIGN_RIGHT)
                  .appendTitle("socket");
              this.appendValueInput("address")
                  .setAlign(Blockly.ALIGN_RIGHT)
                  .appendTitle("address");
              this.setTooltip('');
            }
          };
      };
      
      return routine;
    };
  }
]);