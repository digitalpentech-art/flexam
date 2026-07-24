from .plugins.network import NetworkSimulationPlugin

class SimulationEngine:
    _plugins = {
        'network_sim': NetworkSimulationPlugin
    }

    @classmethod
    def get_plugin(cls, task):
        plugin_class = cls._plugins.get(task.simulation_type)
        if not plugin_class:
            raise ValueError(f"Unknown simulation type: {task.simulation_type}")
        return plugin_class(task)
