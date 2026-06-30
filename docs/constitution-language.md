# Constitution Language (v1)

The Neural Constitution Engine uses a bespoke, pure-Python Expression Language for defining deterministic rules. This language allows operators to write expressive policies without sacrificing security, as it contains no loops, variables, or arbitrary code execution (no `eval` or `exec`).

## Syntax and Grammar

The language follows a standard recursive-descent grammar with C-style boolean logic and Python-style relational operators.

### Data Types
- **Strings:** `'value'` or `"value"`
- **Numbers:** `42`, `-3.14`
- **Booleans:** `true`, `false`
- **Null:** `null`
- **Arrays:** `['a', 'b', 1]`

### Field Access
You can access fields from the `DecisionRequest` object using dot notation:
- `action.type`
- `action.params.environment`
- `context.environment.name`

*Note: If a field does not exist, the engine will safely evaluate it to `null` rather than throwing an exception.*

### Operators

| Operator | Description | Example |
|---|---|---|
| `==`, `=` | Equality | `action.type == 'deploy'` |
| `!=` | Inequality | `action.params.env != 'prod'` |
| `<`, `<=`, `>`, `>=` | Relational | `action.params.vulns <= 0` |
| `and` / `or` | Logical | `A and (B or C)` |
| `not` | Logical Negation | `not action.params.has_rollback` |
| `in` | Array Membership | `action.type in ['deploy', 'build']` |
| `contains` | Collection Contains | `action.params.tags contains 'critical'` |
| `starts_with` | String Prefix | `action.type starts_with 'db.'` |
| `ends_with` | String Suffix | `action.type ends_with '.migrate'` |
| `regex` | Regular Expression Match | `action.type regex '^db\..*'` |
| `exists` | Field Presence | `exists action.params.cab_approved` |

## Example Rules

**Require a rollback plan for production deployments:**
```yaml
condition: "action.type == 'deploy' and action.params.environment == 'production' and not action.params.has_rollback_plan"
```

**Block security vulnerabilities:**
```yaml
condition: "action.type == 'deploy' and action.params.critical_vulns > 0"
```

**Block unauthorized database actions:**
```yaml
condition: "action.type regex '^db\..*' and not exists action.params.manual_approval"
```

## Performance
The engine tokenizes, parses, and evaluates expressions with near-zero latency. A typical policy AST evaluates in **~5 microseconds** per rule.
