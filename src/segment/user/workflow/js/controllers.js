function WorkflowController($scope, $element, routineView, nodeView) {
  var selection = d3.select($element[0]).append("svg"),
      routine = routineView();
    
  selection.call(nodeView());
  
  selection.selectAll(".routine")
    .data([
      {
        "name": "TestSource",
        "type": "source",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestSource",
        "type": "source",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestTarget",
        "type": "target",
        "methods": [
          "testMethod"
          
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestTarget",
        "type": "target",
        "methods": [
          "testMethod"
          
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestCondition",
        "type": "condition",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestCondition",
        "type": "condition",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestEvent",
        "type": "event",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestEvent",
        "type": "event",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestAction",
        "type": "action",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      },
      {
        "name": "TestAction",
        "type": "action",
        "methods": [
          "testMethod"
        ],
        "properties": [
          "testProperty"
        ]
      }
    ])
    .enter().call(routine);
}
