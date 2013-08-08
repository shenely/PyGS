angular.module("workflow.controllers", [])
  .controller("WorkflowController", [
    "$scope",
    "$element",
    "routineView",
    "nodeView",
    function ($scope, $element, routineView, nodeView) {
      var selection = d3.select($element[0]).append("svg"),
          routine = routineView();
        
      selection.call(nodeView());
      
      selection.selectAll(".routine")
        .data([
          {
            "name": "TestSource",
            "type": "source",
            "classed": "routine.TestSource",
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
            "classed": "routine.TestSource",
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
            "classed": "routine.TestTarget",
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
            "classed": "routine.TestTarget",
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
            "classed": "routine.TestCondition",
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
            "classed": "routine.TestCondition",
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
            "classed": "routine.TestEvent",
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
            "classed": "routine.TestEvent",
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
            "classed": "routine.TestAction",
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
            "classed": "routine.TestAction",
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
  ]);
