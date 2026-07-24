class BaseSimulationPlugin:
    def __init__(self, task):
        self.task = task

    def validate_state(self, state_data):
        raise NotImplementedError

    def calculate_score(self, state_data):
        raise NotImplementedError

class NetworkSimulationPlugin(BaseSimulationPlugin):
    def validate_state(self, state_data):
        # Specific logic for network connectivity
        return True

    def calculate_score(self, state_data):
        # Logic to check against scoring_rules in self.task
        return 10
