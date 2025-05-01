class SimulationView:
    def display_kingdom(self, kingdom):
        """Display the current state of the kingdom"""
        print("\n" + "=" * 50)
        print(kingdom)
        # Add more detailed display logic here

    def display_final_results(self, kingdom):
        """Display the final results of the simulation"""
        print("\n" + "=" * 50)
        print("SIMULATION COMPLETE")
        print(f"Total steps: {kingdom.steps}")
        print(f"Total treasures collected: {sum(len(h.stored_treasures) for h in kingdom.hideouts)}")
        print(f"Remaining hunters: {len(kingdom.hunters)}")
        print("=" * 50)

    def get_user_input(self, prompt):
        """Get input from the user"""
        return input(prompt)