import customtkinter
import sys
import pandas as pd
import numpy as np


# Use py2app when you're done with this to turn it into a desktop application

# if you could have a menu where you could select pages to view our dataframe that would be incredible.  Dashboard?  Fuck yeah.

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

root = customtkinter.CTk()
root.geometry("800x500")

root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure((2, 3), weight = 0)
root.grid_rowconfigure((0, 1, 2), weight = 1)


# Functionality + Logic
# - Dummy
def login():
    print("Login ...")

# = = = Update Data = = = #
def UpdateModels(): # Grab the two datasets located in the "update" folder and update scoring models
    pass
def DeleteTodaysPicks() : # Delete any entries from our predictions database whose date is today
    pass

# = = = Make Today's Calculations = = = #
def CalculateChances() : # Use a poisson prediction accompanied by our predicted scores to calculate predicted chance of victory (0-1)
    pass
def CalcMLOdds() : # Use % chance to win/lose to calculate american odds for the moneylines
    pass
# - PullVegasOdds() : Pull live odds from an API and return a list of predictions data !!! This should probably just go in the below function
def UpdatePredictionsWithVegasOdds(): # Add each matchup's vegas odds to our predictions database
    pass

# - - - Display - - - #
# - DisplayTodaysPicks() : Give me all picks today who have value
# - Does Not Exist : Show me all of today's predictions

# Main Frame
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=25, padx=50, fill="both", expand=True)

# Header
label = customtkinter.CTkLabel(master=frame, text="NHL Predictor")
label.pack(pady=12, padx=10)

# - - - Update Data Buttons - - - #
data_frame = customtkinter.CTkFrame(master=frame)
data_frame.pack(pady=10, padx=10, ipady = 10, ipadx = 50)

update_data_label = customtkinter.CTkLabel(master=data_frame, text="Update Data")
update_data_label.pack(pady=5, padx=5)

update_models_button = customtkinter.CTkButton(master=data_frame, text="Update Models", command=UpdateModels)
update_models_button.pack(pady=8, padx=8)

delete_todays_picks_button = customtkinter.CTkButton(master=data_frame, text="Delete Today's Picks", command = DeleteTodaysPicks)
delete_todays_picks_button.pack(pady=8, padx=8)

# - - - Make Calculations Buttons - - - #
calculation_frame = customtkinter.CTkFrame(master=frame)
calculation_frame.pack(pady = 10, padx = 10, ipady = 10, ipadx = 40)

calculation_label = customtkinter.CTkLabel(master=calculation_frame, text="Make Calculations for Today")
calculation_label.pack(pady = 5, padx = 5)

calc_chances_btn = customtkinter.CTkButton(master=calculation_frame, text="Calculate Chances", command = CalculateChances)
calc_chances_btn.pack(pady = 8, padx = 8)

calc_ml_odds_btn = customtkinter.CTkButton(master=calculation_frame, text="Calculate Moneylines", command = CalcMLOdds)
calc_ml_odds_btn.pack(pady = 8, padx = 8)

update_vegas_odds_btn = customtkinter.CTkButton(master = calculation_frame, text = "Update Vegas Odds", command = UpdatePredictionsWithVegasOdds)
update_vegas_odds_btn.pack(pady = 8, padx = 8)

# - - - Display area - - - # For today's picks
todays_picks_frame = customtkinter.CTkFrame(master=root)
todays_picks_frame.pack(pady = 10, padx = 20)

txt = customtkinter.CTkTextbox(master = todays_picks_frame)
txt.pack()

class PrintToTXT(object):
    def write(self, s):
        txt.insert(customtkinter.END, s)

sys.stdout = PrintToTXT()

dframe = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv')
print(dframe)


# Allow user to enter something (A username?)
#entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Anything that you want to submit? A command?") # I guess buttons are the equivalent of a command
#entry1.pack(pady=12, padx=10)

# Button that a user can press to run the login function
#button = customtkinter.CTkButton(master=frame, text="Login", command=login)
#button.pack(pady=12, padx=10)

#checkbox = customtkinter.CTkCheckBox(master=frame, text = "Active")
#checkbox.pack(pady=12, padx=10)


# - - - Positioning - - - #


root.mainloop()