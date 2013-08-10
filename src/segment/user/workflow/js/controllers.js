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
            "name": "ContinuousClock1",
            "type": "source",
            "classed": "epoch.routine.clock.ContinousClock",
            "methods": [
            ],
            "properties": [
              "seed",
              "scale"
            ]
          },
          {
            "name": "SubscribeSocket1",
            "type": "source",
            "classed": "core.routine.socket.SubscribeSocket",
            "methods": [
            ],
            "properties": [
              "socket",
              "address"
            ]
          },
          {
            "name": "SubscribeSocket2",
            "type": "source",
            "classed": "core.routine.socket.SubscribeSocket",
            "methods": [
            ],
            "properties": [
              "socket",
              "address"
            ]
          },
          {
            "name": "PublishSocket1",
            "type": "target",
            "classed": "core.routine.socket.PublishSocket",
            "methods": [
            ],
            "properties": [
              "socket",
              "address",
            ]
          },
          {
            "name": "SplitControl1",
            "type": "target",
            "classed": "core.routine.control.SplitControl",
            "methods": [
            ],
            "properties": [
              "processor"
            ]
          },
          {
            "name": "SplitControl2",
            "type": "target",
            "classed": "core.routine.control.SplitControl",
            "methods": [
            ],
            "properties": [
              "processor"
            ]
          },
          {
            "name": "TestCondition1",
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
            "name": "ParseEpoch1",
            "type": "event",
            "classed": "epoch.routine.ParseEpoch",
            "methods": [
            ],
            "properties": [
            ]
          },
          {
            "name": "ParseEpoch2",
            "type": "event",
            "classed": "epoch.routine.ParseEpoch",
            "methods": [
            ],
            "properties": [
            ]
          },
          {
            "name": "FormatEpoch1",
            "type": "action",
            "classed": "epoch.routine.FormatEpoch",
            "methods": [
            ],
            "properties": [
            ]
          }
        ])
        .enter().call(routine);
    }
  ]);
