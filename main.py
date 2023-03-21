import customtkinter
import pandas as pd
from scipy.stats import poisson
import numpy as np
from datetime import date
import json
import requests

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

# = = = Helper Functions = = = #
# Return a string of today's date
def TodaysDateToString():
    pieces = str(date.today()).split('-')
    yyyy = pieces[0]
    mm = pieces[1]
    dd = pieces[2]
    date_today = [mm.lstrip('0'), dd.lstrip('0'), yyyy[-2] + yyyy[-1]]
    comparison_val = "/".join(date_today)
    return comparison_val
today = TodaysDateToString()

# Return a list of today's matchups from the NHL schedule
def CaptureTodaysGames():
    
    # open our NHL schedule
    schedule_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/schedule.csv')
    
    # define a filter to apply to our schedule that looks for today's date
    filt = ( schedule_df['Date'] == today ) 
        
    # empty list of matchups that will be filled and returned
    todays_matchups = [] 

    for index, row in schedule_df.loc[filt].iterrows(): # apply the filter to our dataframe and iterate over the rows
        # add date and both teams to a dictionary, and add it to the list of items to be returned
        todays_matchups.append( {
            'date': row['Date'],
            'visitor': row['Visitor'],
            'home': row['Home']
        } )

    return todays_matchups

# Return a list of today's matchups from the predictions database
def CaptureTodaysPredictedGames(): 

    # open our predictions database
    predi_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv')
    
    # filter for today
    filt = ( predi_df['Date'] == today )

    # empty list of matchups that will be filled and returned
    todays_matchups = [] 

    for index, row in predi_df.loc[filt].iterrows(): # apply the filter to our dataframe and iterate over the rows | note: remove index?
        # add the information we want to return to our list of todays matchups
        todays_matchups.append({
            'date': row['Date'],
            'visitor': row['AwayTeam'],
            'home': row['HomeTeam'],
            'away_chance': row['away_ml_chance'],
            'home_chance': row['home_ml_chance']
        })
    return todays_matchups

# Calculate expected goals for both teams, for all three models, Return a dictionary with all of the predicted scores
def xG_Calculation(visitor, home):

    # Instantiate our model dataframes and set the index column to team names
    team_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/models/teamstats.csv', index_col='Team')
    exp_5on5_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/models/expectedanalytics.csv', index_col='Team')
    act_5on5_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/models/actualanalytics.csv', index_col='Team')

    # = = = Team Stats Model = = = #
    team_visitor_xg = team_df.loc[visitor, 'AttStr'] * team_df.loc[home, 'DefStr'] * team_df.loc['Avg', 'GFperGame']
    team_home_xg = team_df.loc[home, 'AttStr'] * team_df.loc[visitor, 'DefStr'] * team_df.loc['Avg', 'GFperGame']
    
    # = = = 5on5 Expected Model = = = #
    exp_5on5_visitor_xg = exp_5on5_df.loc[visitor, 'AttStr'] * exp_5on5_df.loc[home, 'DefStr'] * exp_5on5_df.loc['Avg', 'GFperGame']
    exp_5on5_home_xg = exp_5on5_df.loc[home, 'AttStr'] * exp_5on5_df.loc[visitor, 'DefStr'] * exp_5on5_df.loc['Avg', 'GFperGame']

    # = = = 5on5 Actual Model = = = #
    act_5on5_visitor_xg = act_5on5_df.loc[visitor, 'AttStr'] * act_5on5_df.loc[home, 'DefStr'] * act_5on5_df.loc['Avg', 'GFperGame']
    act_5on5_home_xg = act_5on5_df.loc[home, 'AttStr'] * act_5on5_df.loc[visitor, 'DefStr'] * act_5on5_df.loc['Avg', 'GFperGame']

    return { 
        'teamstats':{'visitor_xg': team_visitor_xg, 'home_xg': team_home_xg},
        'exp_5on5':{'visitor_xg': exp_5on5_visitor_xg, 'home_xg': exp_5on5_home_xg},
        'act_5on5':{'visitor_xg': act_5on5_visitor_xg, 'home_xg': act_5on5_home_xg} 
        }

# Leverage the xG_Calculation to predict today's matchups expected outcomes
def Make_Scoring_Predictions_Today():

    # open our predictions database to be updated with all of today's matchups(date, teams, xGoals, odds)
    predi_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv')

    # - Model Attribution - # - How important do you think each model is?
    teamstat_weight = 0.333
    exp_5on5_weight = 0.333
    act_5on5_weight = 0.333

    # check predictions to see if we've already ran today's game
    if today in predi_df['Date'].values:
        return print("Today's predictions have already been made", today)

    # predict Overall Expected Goals for each team
    for matchup in CaptureTodaysGames(): # iterate over each of today's games
        
        xGoals_Raw = xG_Calculation(matchup['visitor'], matchup['home']) # predictions for each of our 3 models
        
        # calculate the overall expected goals for both teams based on how much you attribute to each model
        home_xg_ovr = ( ( xGoals_Raw['teamstats']['home_xg'] * teamstat_weight ) + ( xGoals_Raw['exp_5on5']['home_xg'] * exp_5on5_weight ) + ( xGoals_Raw['act_5on5']['home_xg'] * act_5on5_weight ) )
        visitor_xg_ovr = ( ( xGoals_Raw['teamstats']['visitor_xg'] * teamstat_weight ) + ( xGoals_Raw['exp_5on5']['visitor_xg'] * exp_5on5_weight ) + ( xGoals_Raw['act_5on5']['visitor_xg'] * act_5on5_weight ) )

        # create a Dataframe with 1 row for this matchup, to be added to our predictions dataframe
        entry_df = pd.DataFrame({'Date': [matchup['date']], 'AwayTeam': [matchup['visitor']], 'Away_xG': [visitor_xg_ovr.round(2)], 'HomeTeam': [matchup['home']], 'Home_xG': [home_xg_ovr.round(2)]})
        
        # add it to our predictions database
        predi_df = pd.concat([predi_df, entry_df], ignore_index=True)
        
    # save our predictions to our predictions database
    predi_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv', index=False)
    print(" = = = = Predictions saved = = = = ")
    print("= = = Date, Teams + Exp. Goals = = =")
    print("------------------------------------")

# Pull live odds from an API and return a list of predictions data [ [ {teamA, priceA], [teamB, priceB]} ] ]
def PullVegasOdds():

    key = 'fa8219191b40b3fec426e43e1a7a37b8'
    url = f'https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds?regions=us&oddsFormat=american&apiKey={key}&markets=h2h&bookmakers=draftkings'

    # send a request to our API url
    response = requests.get(url)

    # check to make sure we received a valid response
    if response.ok:
        pass
    else:
        return print("Invalid request")

    # parse our response into json format
    odds_data = json.loads(response.text)

    # for each item in our response, I want to pull the expected outcomes and return a list of teams and their odds
    dk_predictions = []
    for row in odds_data:
        try:
            dk_predictions.append(row['bookmakers'][0]['markets'][0]['outcomes'])
        except:
            pass

    return dk_predictions

# = = = Update Data = = = #
def UpdateModels(): # Grab the two datasets located in the "update" folder and update scoring models
    
        # Open our team stats and analytics tables
        team_stats_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/update/teamstats.csv') 
        analytics_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/update/analytics.csv')

        # Create a new dataframe only with the columns that we want
        new_team_df = team_stats_df[["Team", "GP", "GF/G", "GA/G"]].copy()
        new_analytic_df = analytics_df[["Team", "xGF", "xGA", "aGF", "aGA"]].copy() # create a new frame only with the columns that we want

        # Combine tables 
        new_df = pd.merge(new_team_df, new_analytic_df, on='Team') 

        # Add columns to our table using a calculation
        new_df['5on5_xGF-game'] = new_df.apply(lambda row: row['xGF'] / row["GP"], axis=1) # Use # of xGF / games played to get a per game statistic
        new_df['5on5_xGA-game'] = new_df.apply(lambda row: row['xGA'] / row["GP"], axis=1) # Use # of xGA / games played to get a per game statistic
        new_df['5on5_aGF-game'] = new_df.apply(lambda row: row['aGF'] / row["GP"], axis=1) # Use # of xGF / games played to get a per game statistic
        new_df['5on5_aGA-game'] = new_df.apply(lambda row: row['aGA'] / row["GP"], axis=1) # Use # of xGA / games played to get a per game statistic

        new_df = new_df.rename(columns={"GF/G": "TeamGF-game", "GA/G": "TeamGA-game"}).drop(columns=["xGF", "xGA", "aGF", "aGA"]) # Rename some columns and drop cumulative stats

        new_df.loc['mean'] = new_df.mean(numeric_only=True) # Create a new row where we call mean on each series.  The index is mean 
        new_df.loc['mean', 'Team'] = "Avg" # Update the 'Team' value for our mean row to be Avg

        # Separate our models from eachother
        team_df = new_df[["Team", "TeamGF-game", "TeamGA-game"]].rename(columns={"TeamGF-game": "GFperGame", "TeamGA-game": "GAperGame"}).round(2)
        exp_5on5_df = new_df[["Team", "5on5_xGF-game", "5on5_xGA-game"]].rename(columns={"5on5_xGF-game": "GFperGame", "5on5_xGA-game": "GAperGame"}).round(2)
        act_5on5_df = new_df[["Team", "5on5_aGF-game", "5on5_aGA-game"]].rename(columns={"5on5_aGF-game": "GFperGame", "5on5_aGA-game": "GAperGame"}).round(2)

        # Add attack and defensive strengths to each model
        team_df['AttStr'] = (team_df['GFperGame'] / team_df.loc['mean', 'GFperGame']).round(2)
        team_df['DefStr'] = (team_df['GAperGame'] / team_df.loc['mean', 'GAperGame']).round(2)

        exp_5on5_df['AttStr'] = (exp_5on5_df['GFperGame'] / exp_5on5_df.loc['mean', 'GFperGame']).round(2)
        exp_5on5_df['DefStr'] = (exp_5on5_df['GAperGame'] / exp_5on5_df.loc['mean', 'GAperGame']).round(2)

        act_5on5_df['AttStr'] = (act_5on5_df['GFperGame'] / act_5on5_df.loc['mean', 'GFperGame']).round(2)
        act_5on5_df['DefStr'] = (act_5on5_df['GAperGame'] / act_5on5_df.loc['mean', 'GAperGame']).round(2)

        team_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/models/teamstats.csv', index=False)
        exp_5on5_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/models/expectedanalytics.csv', index=False)
        act_5on5_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/models/actualanalytics.csv', index=False)
        
        print("Models updated successfully")

def DeleteTodaysPicks() : # Delete any entries from our predictions database whose date is today

        today = TodaysDateToString()

        predi_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv') # load our predictions data

        today = TodaysDateToString()

        filt = ( predi_df['Date'] == today ) 

        predi_df.drop(index=predi_df[filt].index, inplace=True) # remove any rows with today's date from our predictions dataset

        predi_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv', index=False)

        print("Today's predictions have been deleted")

# = = = Make Today's Calculations = = = #
def CalculateChances() : # Use a poisson prediction accompanied by our predicted scores to calculate predicted chance of victory (0-1)
    
    # Update the predictions database with today's matchups (date/away/home) and expected goals for each team
    Make_Scoring_Predictions_Today()

    # load in a blank poisson table to load with our chances of winning, as-well as our predictions dataframe
    pssn_table_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/poissontable.csv').drop(columns=['num'])
    predi_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv')
    
    # make sure our chances are float values we can update with decimal chance of winning
    predi_df.loc[:, ['home_ml_chance', 'away_ml_chance']] = predi_df.loc[:, ['home_ml_chance', 'away_ml_chance']].fillna(0.000) 
    
    # check to see if we've already calculated today's games
    filt = ( predi_df['Date'] == today )
    if predi_df.loc[filt, 'home_ml_chance'].values.any() > 0:
        return print("You've already calculated moneyline chances for today's games!")

    for matchup in CaptureTodaysPredictedGames():
        # query our predictions dataframe on both of the teams and the date so that we can grab expected goals for both teams, to be used in our poisson calculation
        home_filt = ( (predi_df['HomeTeam'] == matchup['home']) & (predi_df['Date'] == today ) ) # create a query for the matchup's home team and today's date
        away_filt = ( (predi_df['AwayTeam'] == matchup['visitor']) & (predi_df['Date'] == today ) ) # create a query for the matchup's away team and today's date
        away_xg = predi_df.loc[away_filt, 'Away_xG'] # query away exp goals
        home_xg = predi_df.loc[home_filt, 'Home_xG'] # query home exp goals

        # fill our poisson table dataframe with data based on the likelihood of home/away team scores and expected goal combination occurences
        for i in range(11): # this will be our row value, it will represent the away team's score
            for l in range(11): # this will be our column value, it will represent the home team's score
                
                # for each cell in my dataframe, I want to set it to the likelihood of both team's score outcomes combined
                pssn_table_df.loc[i, f'{l}'] = ( (poisson.pmf(k=i, mu=away_xg) ).item() * ( poisson.pmf(k=l, mu=home_xg) ).item() )
                chance = pssn_table_df.loc[i, f'{l}'].round(3)
                
                # if the outcome is equal, give each team an equal chance at that victory; if home has more points, give them the chance of victory; if away has more points...
                if i == l:
                    predi_df.loc[home_filt, 'home_ml_chance'] += (0.5 * chance)
                    predi_df.loc[home_filt, 'away_ml_chance'] += (0.5 * chance)
                elif l > i:
                    predi_df.loc[home_filt, 'home_ml_chance'] += chance
                elif l < i:
                    predi_df.loc[home_filt, 'away_ml_chance'] += chance

        if predi_df.loc[home_filt, 'home_ml_chance'].item() > 0.5: # is the home team the favorite?
            predi_df.loc[home_filt, 'Home_mlPred'] = np.round( (-1) * ( 100 / ( (1/predi_df.loc[home_filt, 'home_ml_chance'].item() ) - 1 ) ) , 0 ) # home_ml_prediction
            predi_df.loc[away_filt, 'Away_mlPred'] = np.round( ( ( 1/predi_df.loc[home_filt, 'away_ml_chance'].item() ) * 100 ) - 100 , 0 ) # away_ml_prediction
        else: # home team is the underdog
            predi_df.loc[away_filt, 'Away_mlPred'] = np.round( (-1) * ( 100 / ( (1/predi_df.loc[home_filt, 'away_ml_chance'].item() ) - 1 ) ) , 0 ) # away_ml_prediction
            predi_df.loc[home_filt, 'Home_mlPred'] = np.round( ( ( 1/ predi_df.loc[home_filt, 'home_ml_chance'].item() ) * 100 ) - 100 , 0 ) # home_ml_prediction

    # save updates
    predi_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv', index=False)

    return print("Predictions for today saved!")

def UpdatePredictionsWithVegasOdds(): # Add each matchup's vegas odds to our predictions database
    # create a filter to check our predictions database for today's games
    predi_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv')
    date_filt = ( predi_df['Date'] == today ) 

    # check if any of our vegas odds have not been updated for today
    # if they are all updated, do not run anything; return a statement
    if predi_df.loc[date_filt, 'Away_vegasPred'].notnull().any() or predi_df.loc[date_filt, 'Home_vegasPred'].notnull().any():
        return print("You've already updated today's games with Vegas Odds")
    else: # If they have not been updated, pull odds from the api and return an object with today's teams and their odds
        veg_odds = PullVegasOdds()

    # for each matchup, update the away/home teams' vegas odds
    for matchup in veg_odds:
        
        # grab the values we want from each matchup object
        teamA = matchup[0]['name']
        teamA_odds = matchup[0]['price']
        teamB = matchup[1]['name']
        teamB_odds = matchup[1]['price']

        # update each team in today's matchups with vegas' odds, depending on whether they're home or away
        if teamA in predi_df.loc[date_filt, 'AwayTeam'].values:
            teamA_away_filt = ( ( predi_df['AwayTeam'] == teamA ) & ( predi_df['Date'] == today ) ) # filter where teamA is the away team for today's game
            teamB_home_filt = ( ( predi_df['HomeTeam'] == teamB ) & ( predi_df['Date'] == today ) ) # filter where teamB is the home team for today's game
            predi_df.loc[teamA_away_filt, 'Away_vegasPred'] = teamA_odds # Update away vegas odds 
            predi_df.loc[teamB_home_filt, 'Home_vegasPred'] = teamB_odds # Update home vegas odds
        elif teamA in predi_df.loc[date_filt, 'HomeTeam'].values:
            teamB_away_filt = ( ( predi_df['AwayTeam'] == teamB ) & ( predi_df['Date'] == today ) ) # filter where teamB is the away team for today's game
            teamA_home_filt = ( ( predi_df['HomeTeam'] == teamA ) & ( predi_df['Date'] == today ) ) # filter where teamA is the home team for today's game
            predi_df.loc[teamB_away_filt, 'Away_vegasPred'] = teamB_odds # Update away vegas odds
            predi_df.loc[teamA_home_filt, 'Home_vegasPred'] = teamA_odds # Update home vegas odds
        else:
            print(f"{teamA} is not in today's home teams or away teams")

    # save predictions.csv
    predi_df.to_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv', index=False)

    print("Vegas odds for today's games have been added")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x500")
        self.title("NHL Predictor App")
        self.minsize(900, 400)

        # Create a 1x5 grid
        #self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight = 1)

        
        # Table to display today's picks
        self.table_space = customtkinter.CTkTextbox(master=self, bg_color="white")
        self.table_space.grid(row = 0, column = 2, columnspan = 7, rowspan = 10, padx = 20, pady = (20, 0), sticky = "nsew")

        # Update Data Header
        self.data_label = customtkinter.CTkLabel(master=self, text="Update Data")
        self.data_label.grid(row = 0, column = 0, padx = 20, pady = (20, 0), sticky="ew")
        # Update Data Buttons
        self.update_models_button = customtkinter.CTkButton(master = self, text="Update Models", command=UpdateModels)
        self.update_models_button.grid(row = 1, column = 0, padx = 20, pady = 20, sticky = "ew")
        self.delete_todays_picks_button = customtkinter.CTkButton(master = self, text="Delete Today's Picks", command = DeleteTodaysPicks)
        self.delete_todays_picks_button.grid(row = 2, column = 0, padx = 20, pady = 20, sticky = "ew")

        # Calculation Header
        self.calc_label = customtkinter.CTkLabel(master = self, text = "Make Calculations")
        self.calc_label.grid(row = 0, column = 1, padx = 20, pady = (20, 0), sticky = "ew")
        # Calculation Buttons
        self.calc_odds_btn = customtkinter.CTkButton(master = self, text="Calculate Predictions", command = CalculateChances)
        self.calc_odds_btn.grid(row = 1, column = 1, padx = 20, pady = 20, sticky = "ew")
        self.update_vegas_odds_btn = customtkinter.CTkButton(master = self, text = "Pull Vegas Odds", command = UpdatePredictionsWithVegasOdds)
        self.update_vegas_odds_btn.grid(row = 2, column = 1, padx = 20, pady = 20, sticky = "ew")
        
        # Display Header
        self.queries_label = customtkinter.CTkLabel(master = self, text = "Display Data")
        self.queries_label.grid(row = 6, column = 0, columnspan = 2, padx = 20, pady = (20, 0), sticky = "ew")
        # Display Buttons
        self.display_value_today_btn = customtkinter.CTkButton(master = self, text = "Display Today's Picks", command = self.display_todays_picks)
        self.display_value_today_btn.grid(row = 7, column = 0, padx = 20, pady = 20, sticky = "ew")
        self.display_all_today_btn = customtkinter.CTkButton(master = self, text = "Display All of Today's Data")
        self.display_all_today_btn.grid(row = 7, column = 1, padx = 20, pady = 20, sticky = "ew")

    # def button_callback(self):
    #         self.textbox.insert("insert", self.combobox.get() + "\n")

    # Method for displaying today's picks that are valuable
    def display_todays_picks(self):

        today = TodaysDateToString()

        # open our predictions and filter for today's picks
        predi_df = pd.read_csv('/Users/anthonyperpetua/Desktop/development/NHLpredictor/predictions.csv')
        predi_df = predi_df[ predi_df["Date"] == today ]

        # apply the logic we desire to our away teams
        filtered_away_df = predi_df[ ( ( predi_df['Away_mlPred'] < predi_df['Away_vegasPred'] ) & ( predi_df['Away_mlPred'] > 0 ) & ( predi_df['Away_vegasPred'] > 0 ) & ( predi_df['Date'] == today ) ) | ( ( predi_df['Date'] == today ) & ( predi_df['Away_mlPred'] < predi_df['Away_vegasPred'] ) & ( ( predi_df['Away_mlPred'] < 0 ) & ( predi_df['Away_vegasPred'] < 0) ) | ( ( predi_df['Away_mlPred'] < 0 ) & ( predi_df['Away_vegasPred'] > 0 ) ) ) ]
        filtered_away_df = filtered_away_df[['Date', 'AwayTeam', 'Away_mlPred', 'Away_vegasPred']].copy()

        # apply the logic we desire to our home teams
        filtered_home_df = predi_df[ ( ( predi_df['Home_mlPred'] < predi_df['Home_vegasPred'] ) & ( predi_df['Home_mlPred'] > 0 ) & ( predi_df['Home_vegasPred'] > 0 ) & ( predi_df['Date'] == today ) ) | ( ( predi_df['Date'] == today ) &  ( predi_df['Home_mlPred'] < predi_df['Home_vegasPred'] ) & ( ( predi_df['Home_mlPred'] < 0 ) & ( predi_df['Home_vegasPred'] < 0) ) | ( ( predi_df['Home_mlPred'] < 0 ) & ( predi_df['Home_vegasPred'] > 0 ) ) ) ]
        filtered_home_df = filtered_home_df[['Date', 'HomeTeam', 'Home_mlPred', 'Home_vegasPred']].copy()

        # combine our filtered picks
        todays_picks = pd.concat([filtered_away_df, filtered_home_df])

        
        self.table_space.insert("insert", " = = = Today's Picks = = = \n{:^5} - {:<}\n".format("Val", "Team"))
        
        # Build value-picks strings
        for row in todays_picks.index:

            if pd.isna(todays_picks['AwayTeam'][row]):
                team = todays_picks['HomeTeam'][row]
                pred_odds = todays_picks['Home_mlPred'][row]
                veg_odds = todays_picks['Home_vegasPred'][row]
                value = str(abs(abs(pred_odds) - abs(veg_odds))).rstrip(".0")
                entry = "{:^5} - {:<}\n\n".format(str(value), str(team))
            else:
                team = todays_picks['AwayTeam'][row]
                pred_odds = todays_picks['Away_mlPred'][row]
                veg_odds = todays_picks['Away_vegasPred'][row]
                value = str(abs(abs(pred_odds) - abs(veg_odds))).rstrip(".0")
                entry = "{:^5} - {:<}\n\n".format(str(value), str(team))

            # Insert each pick into a textbox
            self.table_space.insert("insert", "{}".format(entry))

        #print(todays_picks.index)
        return print("Displaying today's picks with value")
        #return print(todays_picks)

if __name__ == "__main__":
    app = App()
    app.mainloop()