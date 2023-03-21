Required Packages:
- pandas
- numpy
- scipy.stats (poisson)
- customtkinter
- requests
- json
- datetime (date)


Files:

App 
1. main.py | This is the application, it contains all necessary functions and displays a GUI for the user to utilize

----------

Data (These datasets came from pro-hockey-reference)

2. analytics.csv | This is our first data table, 5on5 Advanced Team Stats

3. teamstats.csv | This is our second data table, Team Stats

4. schedule.csv | This is the current year's NHL schedule

/models

5. actualanalytics.csv | Derived scoring model based on 5on5 actual stats

6. expectedanalytics.csv | Derived scoring model based on 5on5 exp. stats

7. teamstats.csv | "Expected" statistics provided from the dataset


----------

Statistics

8. poissontable.csv | Blank table I created that will be populated with the likelihood of each outcome for each matchup

----------

/Archive

9. These are all initial iterations and work of me developing "main.py"

----------


Details

This scoring model was taught to me by Action Backers, a sports analytics platform; with the intention of using publicly available data to predict the likelihood of outcomes for Hockey matches.  Only the model was taught on google sheets, and required lots of time consuming data entry.

The model uses the advanced metric, Expected Goals per-game to give each team an Attack Strength and Defensive Strength Scores.  This is calculated by dividing each team's expected goals (for or against respectively) and dividing it by the (for or against respectively) league average.  This will show you how each team fares compared to the rest of the teams; and it will also give you how many goals each team typically scores or allows, when multiplying it by the league average.

Example:
- Boston Bruins - (xGF) expected goals for: 3.78/game  |  (xGA) expected goals against: 2.13/game
    - This means that the Bruins are expected to score 3.78 goals per game and allow 2.13 goals per game.  
        - If we divide the bruins xGF by the league's average xGF (3.2), we get the Bruin's Attack Strength: 1.18
        - If we divide the bruins xGA by the league's average xGA (3.05), we get the Bruin's Defensive Strength: 0.698
- Meaning that the bruins on average score 18% more points and allow 30% less points than the typical team.  In other words, the Bruins are a great Hockey team (Currently the best in the league)
    - Good team:  High points for, Low points allowed
    - Bad team:  Low points for, High points allowed
    - Fun team:  High points for, High points allowed
    - Boring team:  Low points for, Low points allowed

We are going to use the provided Expected Goals metric from the Team Statistics Dataset, and we will calculate Expected Goals and Actual Goals for/against from the 5on5 Advanced Statistics dataset.  Use the number of games played by each team from the Team Statistics dataset to make per game calculations.  
- Calculate attack/defensive strengths for each data segmentation; and then we will aggregate the scores afterwards
- ! Note: I plan to write a script(s) that will run my program through the entire NHL schedule of games that have already been played this year; making predictions for each game and at the end, calculating the error (The difference between the actual outcome and the predicted outcomes).  I would like it to perform this test numerous times, adjusting the weights of each scoring model to find the combination with the greatest accuracy.


My intent is to make predictions for the games that occur today, so I will use the schedule.csv file to determine which games are being played today, and who is playing in them

To calculate each team's score:
- Multiply attack strength (how many goals above/below average the team scores per game) by the opponent's defensive strength (how many goals above/below average the opponent allows per game) by the league average goals for per game (how many goals each team scores per game).  Do this with each of the three models for each team and aggregate the team's scores
    - Away xG = Away xGF * Home xGA * LeagueAvg xGF
    - Home xG = Home xGF * Away xGA * LeagueAvg xGF

Once we have an Expected outcome for each matchup, we can use a poisson distribution to predict the likelihood of each outcome in an NHL game, 0-10 points for both teams.  
- The poisson distribution takes the team's expected score and says, 
    - If you'd typically score this many points, what is the likelihood that you score [as many points as the current iteration has this team scoring]?  
- At each iteration (each possible outcome, i.e. 3-1, 0-1, 9-9) we take that likelihood of occurence and we add it to the winning team's chance of victory.  After completing the 100 iterations, we have each team's % chance of victory 
    - If the score is 3-1 meaning that the Away team won by a margin of 2 points, and there's a 4% chance of this outcome happening.  We add 4% to the away team's chance of winning.  
    - If the score is a tie (i.e. 3-3) the game will go to a shootout and each team has an equal opportunity at winning; so each team will get 50% of the chance of victory from that outcome.  So if there is a 4% chance that each team will score 4 points, we add 2% to both team's chance of victory before moving onto the next iteration
- Do this for every possible outcome from 0-0 up to 10-10

Once we have each team's chance of winning, we will use it to determine who is the favorite/underdog and in turn, the predicted odds for each team
- You can lookup (or see in my code) the formulas for converting % chance of victory to american odds or decimal odds; depending on which you use.  I use American odds, so that is what I am converting to, where the favorite has greater than a 50% chance of victory and their odds are negative indicating that if you were to bet $10, you will win some amount less than $10; and the opposite is true for the underdog.
- These american odds represent predictions for each game and will be stored in our predictions database

Next, send a request to The Odds API, parse the response, and return odds from the book of your choice to be compared with our predicted odds
- Save these bookmaker odds to the predictions database and we are ready to compare

Finally, look through each matchup in today's games and if the price provided by your book is better than the predicted price; it means that your model predicts the team to have a better chance of winning than your book thinks; and that there's an edge for you to take.
- For example, if your model says that the Philadelphia Flyers have a 50% chance of winning, this is the equivalent of +100 odds.  In other words, you risk $10 with the chance to win $10.  A fair bet.  
    - But if the book (wrongly) says that the flyers have a 40% chance of winning (~ +200), you are offered the wager of risk $10 to possibly win $20.  
    - If you were flipping a coin with someone (50% likelihood of tails/heads) where you win $20 for each outcome where the coin lands on heads, but only pay $10 for each tails outcome.  Wouldn't you play that game forever?  Casinos do not offer wagers like this because they only offer wagers that are in their favor.  Our goal here is to identify favorable/unfavorable offers with the intention of capitalizing on favorable ones, and avoiding unfavorable ones.

---------

Main Idea:
- The key here is that the model is predicting outcomes and expected scores.  But it is not exactly saying that a team will win.  It is making recomendations based on value.  If a team has a 25% chance of victory, but is wrongly priced at 10% chance of victory; this would be incredible value.  There's a much much better chance of something happening, than the pricemakers believe.  But it does not mean that it is likely to happen.  There is still only a 25% chance of this happening, which is low.  The idea is to find edges, misprices in the market day after day, which is part of the reason we're using NHL.  It's a predictable sport, there are games everyday, we've got great metrics to use to build the model, it's low scoring, the outcome is simple, it's just great for our purpose. 

----------

Instructions

- I recommend updating your models weekly so that the predictions you make leverage the most recent and accurate data

When you run main.py you'll want to run, 

- "Calculate Predictions" and then "Pull Vegas Odds"
- - After this you can click "Display Today's Picks" and each of today's picks that contain value will appear in the box on the right, as-well as the magnitude of price discrepancy (Larger is better)
- "Display All of Today's Data" is not currently available as I need a more efficient way to display a table of data in my GUI; and I currently have a number of other priorities that are more important.  If you want to see it, you can go in the /Archive directory and go to run.ipynb.  Look for the cell that has a filter for today's date, opens the predictions database and displays the dataframe with filter applied.  You can also just open the csv file with Excel or Numbers and look at the rows that contain today's date
- Update Models:  
- - Download the excel copy of each table from pro-hockey-reference | current season summary | team statistics and team analytics (5-on-5)
- - Delete the first row and update the column header to "Team" in column B  
- - Save each dataset in the update folder, as a csv file named, "analytics.csv" or "teamstats.csv" depending on which you are accessing
- - Run the update models button
- Delete Today's Picks:  If you want to re-run today's predictions for whatever reason, this will delete any rows from your predictions database whose date is today