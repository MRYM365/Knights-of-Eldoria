from controller.simulation_controller import SimulationController
import tkinter as tk
from tkinter import scrolledtext
import sys
from typing import TYPE_CHECKING

# Add this import
from model.hunter import HunterSkill

if TYPE_CHECKING:
    from model.hideout import Hideout
    from model.hunter import Hunter
    from model.knight import Knight
    from model.treasure import Treasure

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eldoria Treasure Hunt")

        # Create controller with fixed size
        self.controller = SimulationController(size=20)

        # Setup UI
        self.setup_ui()

        # Initialize simulation
        self.controller.initialize_simulation(
            num_hideouts=20,
            num_hunters=35,
            num_knights=30,
            num_treasures=80
        )

        # Start simulation
        self.run_simulation()

    def update_stats_display(self):
        kingdom = self.controller.kingdom
        wealth = sum(len(h.stored_treasures) for h in kingdom.hideouts)

        self.stats_labels['step'].config(text=f"Step: {kingdom.steps}")
        self.stats_labels['hunters'].config(text=f"Hunters: {len(kingdom.hunters)}")
        self.stats_labels['knights'].config(text=f"Knights: {len(kingdom.knights)}")
        self.stats_labels['treasures'].config(text=f"Treasures: {len(kingdom.treasures)}")
        self.stats_labels['wealth'].config(text=f"Total Wealth: {wealth}")

        # Add more stats if needed
        # self.stats_labels['active_knights'].config(text=f"Active Knights: {sum(1 for k in kingdom.knights if k.energy > 20)}")

    def show_agent_details(self, event):
        kingdom = self.controller.kingdom
        cell_size = 600 // kingdom.size
        x, y = event.x // cell_size, event.y // cell_size

        agent = kingdom.grid[x][y]
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)

        if agent is None:
            self.details_text.insert(tk.END, "Empty cell\n")
            self.details_text.insert(tk.END, f"Location: ({x}, {y})")
        else:
            self.details_text.insert(tk.END, str(agent) + "\n\n")
            if hasattr(agent, 'stamina'):
                self.details_text.insert(tk.END, f"Stamina: {agent.stamina:.1f}%\n")
            if hasattr(agent, 'energy'):
                self.details_text.insert(tk.END, f"Energy: {agent.energy:.1f}%\n")
            if hasattr(agent, 'value'):
                self.details_text.insert(tk.END, f"Value: {agent.value:.1f}%\n")

        self.details_text.config(state='disabled')

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for visualization (left side)
        self.canvas = tk.Canvas(main_frame, width=600, height=600, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)



        # Right panel for information display
        right_panel = tk.Frame(main_frame, width=250, padx=10, pady=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        # Simulation stats
        stats_frame = tk.LabelFrame(right_panel, text="Simulation Stats", padx=5, pady=5)
        stats_frame.pack(fill=tk.X, pady=5)

        self.stats_labels = {
            'step': tk.Label(stats_frame, text="Step: 0", anchor='w'),
            'hunters': tk.Label(stats_frame, text="Hunters: 0", anchor='w'),
            'knights': tk.Label(stats_frame, text="Knights: 0", anchor='w'),
            'treasures': tk.Label(stats_frame, text="Treasures: 0", anchor='w'),
            'wealth': tk.Label(stats_frame, text="Total Wealth: 0", anchor='w')
        }

        for label in self.stats_labels.values():
            label.pack(fill=tk.X, pady=2)

        # Legend
        legend_frame = tk.LabelFrame(right_panel, text="Legend", padx=5, pady=5)
        legend_frame.pack(fill=tk.X, pady=5)

        legend_items = [
            ("Hideout", "#8B4513"),
            ("Hunter (carrying)", "#4682B4"),
            ("Hunter (empty)", "#87CEEB"),
            ("Knight (active)", "#FF6347"),
            ("Knight (resting)", "#FFA07A"),
            ("Bronze Treasure", "#CD7F32"),
            ("Silver Treasure", "#C0C0C0"),
            ("Gold Treasure", "#FFD700")
        ]

        for text, color in legend_items:
            frame = tk.Frame(legend_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, bg=color, width=3, height=1).pack(side=tk.LEFT)
            tk.Label(frame, text=text, anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Agent details and console
        details_frame = tk.LabelFrame(right_panel, text="Event Log", padx=5, pady=5)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            width=30,
            height=15,
            wrap=tk.WORD,
            state='disabled'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Redirect stdout to console
        sys.stdout = TextRedirector(self.details_text, "stdout")

    def run_simulation(self):
        if not self.controller.kingdom.is_simulation_over():
            self.controller.step_simulation()
            self.draw_kingdom()
            self.update_stats_display()  # Add this line
            self.root.after(500, self.run_simulation)
        else:
            self.log.insert(tk.END, "\nSIMULATION COMPLETE\n")

    def draw_kingdom(self):
        self.canvas.delete("all")
        kingdom = self.controller.kingdom
        cell_size = 600 // kingdom.size

        # Draw grid lines
        for i in range(kingdom.size + 1):
            self.canvas.create_line(0, i * cell_size, 600, i * cell_size, fill="gray90")
            self.canvas.create_line(i * cell_size, 0, i * cell_size, 600, fill="gray90")

        # Draw terrain background
        for x in range(kingdom.size):
            for y in range(kingdom.size):
                x1, y1 = x * cell_size, y * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size

                # Alternate background colors for checkerboard pattern
                if (x + y) % 2 == 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#f0f0f0", outline="")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline="")

        # Draw agents
        for x in range(kingdom.size):
            for y in range(kingdom.size):
                x1, y1 = x * cell_size, y * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

                agent = kingdom.grid[x][y]
                if agent is not None:
                    # Hideout visualization
                    if hasattr(agent, 'hunters'):  # Hideout
                        # Castle-like structure
                        self.canvas.create_rectangle(
                            x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                            fill="#8B4513", outline="black", width=1
                        )
                        self.canvas.create_polygon(
                            x1 + 5, y1 + 5, center_x, y1, x2 - 5, y1 + 5,
                            fill="#A0522D", outline="black", width=1
                        )
                        # Hunter count indicator
                        self.canvas.create_text(
                            center_x, center_y,
                            text=str(len(agent.hunters)),
                            fill="white",
                            font=("Arial", 8, "bold")
                        )

                    # Hunter visualization
                    elif hasattr(agent, 'skill'):  # Hunter
                        # Base circle
                        self.canvas.create_oval(
                            x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                            fill="#4682B4" if agent.carrying else "#87CEEB",
                            outline="black", width=1
                        )
                        # Eye indicator
                        eye_x = center_x - 3 if agent.skill == HunterSkill.NAVIGATION else center_x + 3
                        self.canvas.create_oval(
                            eye_x - 2, center_y - 2, eye_x + 2, center_y + 2,
                            fill="white", outline="black", width=1
                        )
                        # Treasure indicator if carrying
                        if agent.carrying:
                            self.canvas.create_oval(
                                center_x - 4, center_y + 5, center_x + 4, center_y + 10,
                                fill={
                                    "BRONZE": "#CD7F32",
                                    "SILVER": "#C0C0C0",
                                    "GOLD": "#FFD700"
                                }[agent.carrying.type.name],
                                outline="black", width=1
                            )

                    # Knight visualization
                    elif hasattr(agent, 'energy'):  # Knight
                        # Armor color based on energy
                        armor_color = "#FF6347" if agent.target else "#FFA07A"
                        # Helmet
                        self.canvas.create_polygon(
                            center_x, y1 + 5,
                                      x1 + 5, center_y,
                                      x2 - 5, center_y,
                            fill=armor_color, outline="black", width=1
                        )
                        # Body
                        self.canvas.create_rectangle(
                            x1 + 10, center_y, x2 - 10, y2 - 5,
                            fill=armor_color, outline="black", width=1
                        )
                        # Energy indicator
                        energy_width = int((x2 - x1 - 20) * (agent.energy / 100))
                        self.canvas.create_rectangle(
                            x1 + 10, y2 - 8, x1 + 10 + energy_width, y2 - 5,
                            fill="#32CD32", outline=""
                        )

                    # Treasure visualization
                    elif hasattr(agent, 'type'):  # Treasure
                        # Treasure chest
                        self.canvas.create_rectangle(
                            x1 + 8, y1 + 12, x2 - 8, y2 - 8,
                            fill={
                                "BRONZE": "#CD7F32",
                                "SILVER": "#C0C0C0",
                                "GOLD": "#FFD700"
                            }[agent.type.name],
                            outline="black", width=1
                        )
                        # Treasure lid
                        self.canvas.create_arc(
                            x1 + 8, y1 + 5, x2 - 8, y1 + 20,
                            start=0, extent=180,
                            fill="#8B4513", outline="black", width=1
                        )
                        # Value indicator
                        value_text = f"{agent.value:.0f}%"
                        self.canvas.create_text(
                            center_x, center_y + 5,
                            text=value_text,
                            fill="black",
                            font=("Arial", 6)
                        )

        # Draw step counter
        self.canvas.create_text(
            10, 10,
            text=f"Step: {kingdom.steps}",
            anchor="nw",
            fill="black",
            font=("Arial", 10, "bold")
        )



class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(tk.END)

    def flush(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()