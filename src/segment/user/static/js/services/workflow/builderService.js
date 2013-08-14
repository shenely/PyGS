var workflowServices = workflowServices || angular.module('workflow.services', []);

workflowServices.factory("builderService", [
  function () {
    return function () {
      var tree = function (selection) {
        var routine = selection.selectAll(".routine"),
            link = selection.selectAll(".link");
        
        routine.selectAll(".source").each(function () {
          var source = d3.select(this),
              output = source.selectAll(".output .node");
          
          output.each(function () {
            var self = this,
                nodes = link
                  .filter(function (d) { return d.source == self; })
                  .map(function (d) { return d.target; }),
                targets = routine.filter(function () {
                  return d3.select(this).selectAll(".input .node")
                           .filter(function () { return this in nodes; })
                           .empty();
                });
          });
        });
      };
      
      return tree;
      
      var example = {
        "application": [
          {
            "name": "",
            "behavior": [
              {
                "name": "",
                "object": [
                  {
                    "name": "",
                    "property": [
                      ""
                    ],
                    "method": [
                      ""
                    ]
                  }
                ],
                "scenario": [
                  {
                    "name": "",
                    "source": [],
                    "event": [],
                    "condition": [],
                    "action": [],
                    "target": []
                  }
                ]
              }
            ]
          }
        ]
      }
    };
  }
]);
