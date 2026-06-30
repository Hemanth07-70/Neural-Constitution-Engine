# Plugin Development

NCE's plugin architecture allows you to dynamically register custom sinks and evaluators without touching core code.

## Defining a Plugin
Simply inherit from `PluginBase` and implement `register`:

```python
from backend.core.plugins.plugin import PluginBase
from backend.core.rules.registry import RuleRegistry

class WebhookAuditPlugin(PluginBase):
    def register(self, registry: RuleRegistry) -> None:
        # Bind custom sinks or resolvers
        pass
```

## Loading Plugins
Point the `PluginManager` to your plugin directory:

```python
from backend.core.plugins.manager import PluginManager

manager = PluginManager()
manager.load_directory("path/to/plugins")
```
