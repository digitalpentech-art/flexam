import importlib
import logging

class SimulationEngine:
    """Backward compatibility class for simulation engine."""
    @staticmethod
    def evaluate(simulation_type, content):
        return evaluate_simulation(simulation_type, content)

def evaluate_simulation(simulation_type, content):
    """
    Dynamically loads and calls the appropriate simulation evaluator plugin.
    
    Plugins are expected to be in app.simulations.plugins.<simulation_type>
    and implement an evaluate(content) function.
    """
    try:
        # Assumes plugins are named after simulation_type
        module_path = f'app.simulations.plugins.{simulation_type}'
        plugin = importlib.import_module(module_path)
        
        if hasattr(plugin, 'evaluate'):
            return plugin.evaluate(content)
        else:
            logging.error(f"Plugin {module_path} does not implement evaluate()")
            return 0.0
            
    except (ImportError, AttributeError) as e:
        logging.error(f"Error loading simulation plugin {simulation_type}: {e}")
        return 0.0
