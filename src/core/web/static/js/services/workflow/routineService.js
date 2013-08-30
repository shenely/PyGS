var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("routineService", [
  function () {
    Blockly.Language["engine_App"] = {
      category: "engine",
      init: function() {
        this.setColour(0);
        this.appendDummyInput()
            .appendTitle("App:")
            .appendTitle(new Blockly.FieldTextInput("description"), "description");
        this.appendStatementInput("story")
            .setCheck("story")
            .appendTitle("stories");
      }
    };
    
    Blockly.Language["engine_Story"] = {
      category: "engine",
      init: function() {
        this.setColour(0);
        this.appendDummyInput()
            .appendTitle("Story:")
            .appendTitle(new Blockly.FieldTextInput("description"), "description");
        this.appendStatementInput("rule")
            .setCheck(["rule"])
            .appendTitle("rules");
        this.appendStatementInput("node")
            .setCheck(["routine"])
            .appendTitle("routines");
        this.setPreviousStatement(true, ["story"]);
        this.setNextStatement(true, ["story"]);
      }
    };
    
    Blockly.Language["engine_Rule"] = {
      category: "engine",
      init: function() {
        this.setColour(0);
        this.appendDummyInput()
            .appendTitle("Rule:")
            .appendTitle(new Blockly.FieldTextInput("description"), "description");
        this.appendStatementInput("clause")
            .setCheck("rule");
        this.setPreviousStatement(true, ["rule"]);
        this.setNextStatement(true, ["rule"]);
      }
    };
    
    Blockly.Language["clause_From"] = {
      category: "clause",
      init: function() {
        this.setColour(90);
        this.appendValueInput("source")
            .setCheck(["clause"])
            .appendTitle("From:")
            .appendTitle("source");
        this.setPreviousStatement(true, ["rule"]);
        this.setNextStatement(true, ["clause"]);
      }
    };
    
    Blockly.Language["clause_When"] = {
      category: "clause",
      init: function() {
        this.setColour(90);
        this.appendValueInput("event")
            .setCheck(["routine"])
            .appendTitle("When:")
            .appendTitle("event");
        this.setPreviousStatement(true, ["rule", "clause"]);
        this.setNextStatement(true, ["clause"]);
      }
    };
    
    Blockly.Language["clause_Given"] = {
      category: "clause",
      init: function() {
        this.setColour(90);
        this.appendValueInput("condition")
            .setCheck(["routine"])
            .appendTitle("Given:")
            .appendTitle("condition");
        this.setPreviousStatement(true, ["rule", "clause"]);
        this.setNextStatement(true, ["clause"]);
      }
    };
    
    Blockly.Language["clause_Then"] = {
      category: "clause",
      init: function() {
        this.setColour(90);
        this.appendValueInput("action")
            .setCheck(["routine"])
            .appendTitle("Then:")
            .appendTitle("action");
        this.setPreviousStatement(true, ["rule", "clause"]);
        this.setNextStatement(true, ["clause"]);
      }
    };
    
    Blockly.Language["clause_To"] = {
      category: "clause",
      init: function() {
        this.setColour(90);
        this.appendValueInput("target")
            .setCheck(["routine"])
            .appendTitle("To:")
            .appendTitle("target");
        this.setPreviousStatement(true, ["rule", "clause"]);
      }
    };
    
    Blockly.Language["clause_And"] = {
      category: "clause",
      init: function() {
        this.setColour(90);
        this.appendValueInput("routine")
            .setCheck(["routine"])
            .appendTitle("And:")
            .appendTitle("routine");
        this.setPreviousStatement(true, ["routine"]);
        this.setNextStatement(true, ["routine"]);
      }
    };
  
    Blockly.Language["statement_Routine"] = {
      category: "statement",
      init: function() {
        this.setColour(180);
        this.appendDummyInput()
            .appendTitle("routine");
        this.setPreviousStatement(true, ["routine"]);
        this.setNextStatement(true, ["routine"]);
      }
    };
  
  Blockly.Language["statement_Clause"] = {
    category: "statement",
    init: function() {
      this.setColour(180);
      this.appendValueInput("clause")
          .setCheck(["clause"])
          .appendTitle("clause");
      this.setOutput(true, ["clause"]);
    }
  };
  
  Blockly.Language["statement_Require"] = {
    category: "statement",
    init: function() {
      this.setColour(180);
      this.appendDummyInput()
          .appendTitle("require");
      this.setOutput(true, ["require"]);
    }
  };
  
  Blockly.Language["statement_Provide"] = {
    category: "statement",
    init: function() {
      this.setColour(180);
      this.appendValueInput("provide")
          .setCheck(["provide", "property", "method"])
          .appendTitle("provide");
      this.setOutput(true, ["provide"]);
    }
  };
    
    return function (data) {
      var datum = data[data.length-1];
      
      Blockly.Language[datum.name] = {
          category: datum.type,
          init: function() {
            this.setColour(270);
            this.appendDummyInput()
                .appendTitle(datum.type + ":")
                .appendTitle(datum.name);
            this.appendDummyInput()
                .appendTitle(new Blockly.FieldTextInput("description"), "description");
            this.appendStatementInput("sat")
                .setCheck(["routine"]);
            this.appendValueInput("socket")
                .setCheck(["require", "provide"])
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendTitle("socket");
            this.appendValueInput("address")
                .setCheck(["require", "provide"])
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendTitle("address");
            this.setPreviousStatement(true, ["routine"]);
            this.setNextStatement(true, ["routine"]);
          }
      };
    };
  }
]);