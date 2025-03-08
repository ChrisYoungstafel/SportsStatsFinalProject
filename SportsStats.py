import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Get where script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Sets file path
FILE_PATH = os.path.join(BASE_DIR, "team_stats.csv")

# Reads the file
df = pd.read_csv(FILE_PATH)

# Class to represent a team's offensive performance stats
class TeamStats:
    # Initialize team stats
    def __init__(self, year, team, wins, losses, points_for, total_yards, pass_yards, rush_yards, turnovers):
        self.year = year
        self.team = team
        self.wins = wins
        self.losses = losses
        self.points_for = points_for
        self.total_yards = total_yards
        self.pass_yards = pass_yards
        self.rush_yards = rush_yards
        self.turnovers = turnovers

    # Getter for team win-loss record
    def win_loss_record(self):
        return f"{self.wins}-{self.losses}"

    # Getter for points per game by season length
    def scoring_efficiency(self):
        if self.year >= 2021:
            games = 17
        else:
            games = 16
        return round(self.points_for / games, 2)

# Class to load and process team stats from the csv
class DataManager:
    # Constructor to read csv and load into Pandas DataFrame
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)

        # Gets a list of team names
        self.teams = sorted(self.df["team"].unique().tolist())

        # Gets a list of sorted years
        self.years = sorted(self.df["year"].unique().tolist(), reverse=True)

    # Getter to get the offensive stats and year
    def get_team_stats(self, team_name, year):
        team_data = self.df[(self.df["team"] == team_name) & (self.df["year"] == year)]
        if team_data.empty:
            return None
        
        # Gets the first row of the filtered data
        row = team_data.iloc[0]
        return TeamStats(row["year"], row["team"], row["wins"], row["losses"], row["points_for"], 
                         row["total_yards_offense"], row["pass_yards"], row["rush_yards"], row["turnovers"])

# Class to create the GUI
class KPIComparatorGUI:
    # Constructor sets up GUI and connects to DataManager
    def __init__(self, root, data_manager):
        self.root = root
        self.data_manager = data_manager
        self.root.title("Team Offensive KPI Comparator")

        # Set to full screen to make everything look better
        self.root.state('zoomed')

        # Frame for selection
        frame_top = tk.Frame(root)
        frame_top.pack(pady=20)

        tk.Label(frame_top, text="Select Year:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
        self.year_var = tk.StringVar()
        self.year_dropdown = ttk.Combobox(frame_top, textvariable=self.year_var, values=self.data_manager.years, state="readonly", width=10)
        self.year_dropdown.grid(row=0, column=1, padx=10, pady=5)
        self.year_var.set(self.data_manager.years[0])

        tk.Label(frame_top, text="Select Team 1:", font=("Arial", 14)).grid(row=0, column=2, padx=10, pady=5)
        self.team1_var = tk.StringVar()
        self.team1_dropdown = ttk.Combobox(frame_top, textvariable=self.team1_var, values=self.data_manager.teams, state="readonly", width=20)
        self.team1_dropdown.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(frame_top, text="Select Team 2:", font=("Arial", 14)).grid(row=0, column=4, padx=10, pady=5)
        self.team2_var = tk.StringVar()
        self.team2_dropdown = ttk.Combobox(frame_top, textvariable=self.team2_var, values=self.data_manager.teams, state="readonly", width=20)
        self.team2_dropdown.grid(row=0, column=5, padx=10, pady=5)

        self.compare_button = tk.Button(root, text="Compare", font=("Arial", 14, "bold"), command=self.compare_teams)
        self.compare_button.pack(pady=10)

        self.result_label = tk.Label(root, text="", font=("Arial", 14), justify="center")
        self.result_label.pack(pady=10)

        # Frame for charts
        self.chart_frame = tk.Frame(root)
        self.chart_frame.pack(fill="both", expand=True)

        # Exit button
        self.exit_button = tk.Button(root, text="End Program", font=("Arial", 14, "bold"), command=self.exit_program, bg="red", fg="white")
        self.exit_button.pack(pady=20)

    # Getter to get user input in the drop down boxes
    def compare_teams(self):
        year = int(self.year_var.get())
        team1_name = self.team1_var.get()
        team2_name = self.team2_var.get()

        # Makes sure both teams are selected
        if not team1_name:
            messagebox.showerror("Error", "Please select both teams.")
            return

        if not team2_name:
            messagebox.showerror("Error", "Please select both teams.")
            return

        team1 = self.data_manager.get_team_stats(team1_name, year)
        team2 = self.data_manager.get_team_stats(team2_name, year)

        # Make sure data was found for the selected teams
        if not team1:
            messagebox.showerror("Error", "Data not found for selected teams and year.")
            return

        if not team2:
            messagebox.showerror("Error", "Data not found for selected teams and year.")
            return

        # Dictionary to store KPIs for the two teams
        comparison = {
            "Win/Loss Record": (team1.win_loss_record(), team2.win_loss_record()),
            "Points Per Game": (team1.scoring_efficiency(), team2.scoring_efficiency()),
            "Total Yards": (team1.total_yards, team2.total_yards),
            "Passing Yards": (team1.pass_yards, team2.pass_yards),
            "Rushing Yards": (team1.rush_yards, team2.rush_yards),
            "Turnovers": (team1.turnovers, team2.turnovers),
        }

        # Summary text
        result_text = f"Comparison of {team1_name} vs {team2_name} ({year}):\n"
        
        # Add a dash line between results and summary
        result_text += "-" * 50 + "\n"

        # Loops through each KPI in the dictionary
        for kpi, (val1, val2) in comparison.items():
            result_text += f"{kpi}: {team1_name} ({val1}) vs {team2_name} ({val2})\n"

        # Update text of self.result_label in GUI
        self.result_label.config(text=result_text)

        # Display graphs by calling self.show_charts()
        self.show_charts({k: v for k, v in comparison.items() if k != "Win/Loss Record"}, team1_name, team2_name)

    # Getter uses Matplotlib to draw charts in GUI
    def show_charts(self, comparison, team1_name, team2_name):
        # Clear out any old stuff
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        labels = list(comparison.keys())
        team1_values = [v[0] for v in comparison.values()]
        team2_values = [v[1] for v in comparison.values()]

        # Title for graphs section
        fig, axs = plt.subplots(1, 5, figsize=(25, 4))
        fig.suptitle(f"Offensive KPI Comparison: {team1_name} vs {team2_name}", fontsize=16)

        # Loops through each KPI and creates a chart
        for i in range(5):
            axs[i].bar([team1_name, team2_name], [team1_values[i], team2_values[i]], color=["blue", "red"])
            axs[i].set_title(labels[i], fontsize=10)
            axs[i].tick_params(axis='x', rotation=45)

        # Prevent overlap
        plt.tight_layout()

        # Create a Matplotlib canvas to display the figure inside the Tkinter GUI
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        
        # Converts Matplotlib canvas to Tkinter widget
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Render the Graph
        canvas.draw()

    # Method to exit program
    def exit_program(self):
        self.root.quit()

# Run GUI
if __name__ == "__main__":
    # Create the Tkinter window
    root = tk.Tk()

    # Load the csv file
    data_manager = DataManager(FILE_PATH)

    # Build the interface
    app = KPIComparatorGUI(root, data_manager)

    # Starts the GUI loop
    root.mainloop()