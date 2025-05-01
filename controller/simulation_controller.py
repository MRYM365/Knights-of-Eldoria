from model.kingdom import Kingdom
import logging


class SimulationController:
    def __init__(self, size=20):
        self.kingdom = Kingdom(size)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%H:%M:%S',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('eldoria_simulation.log')
            ]
        )
        self.logger = logging.getLogger('EldoriaSim')
        self.logger.info("=== Simulation Started ===")

    def initialize_simulation(self, num_hideouts=20, num_hunters=20, num_knights=15, num_treasures=50):
        self.kingdom.initialize(
            num_hideouts=num_hideouts,
            num_hunters=num_hunters,
            num_knights=num_knights,
            num_treasures=num_treasures
        )
        self.logger.info(f"Initialized {self.kingdom.size}x{self.kingdom.size} kingdom with:")
        self.logger.info(f"- {num_hideouts} hideouts")
        self.logger.info(f"- {num_hunters} hunters")
        self.logger.info(f"- {num_knights} knights")
        self.logger.info(f"- {num_treasures} treasures")

    def step_simulation(self):
        self.kingdom.step()
        self.log_status()

    def log_status(self):
        stats = self.kingdom
        self.logger.info(
            f"Step {stats.steps}: "
            f"Hunters: {len(stats.hunters)}, "
            f"Knights: {len(stats.knights)}, "
            f"Treasures: {len(stats.treasures)}, "
            f"Total Wealth: {sum(len(h.stored_treasures) for h in stats.hideouts)}"
        )