# Troubleshooting

### Error: `Rule condition must be an object or string`
Make sure you are not passing a list or integer as the condition of your rule. Conditions must be either a legacy literal-match object or an Expression Language string.

### Error: `Evaluation error`
Check that your `condition` string matches the correct schema paths and that the fields you are referencing exist on the `action.params` or `context` objects. Missing fields evaluate to `null` which can cause logic issues if expected to be booleans.

### DAG Validation Failure
If evaluating an execution plan fails immediately, check for circular dependencies in the graph (i.e. node A depends on node B, which depends on node A). NCE will strictly block cyclic logic.
