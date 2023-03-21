Files:

App 
1. main.py | This is the application, it contains all necessary functions and displays a GUI for the user to utilize

Data (These datasets came from pro-hockey-reference)
2. analytics.csv | This is our first data table, 5on5 Advanced Team Stats
3. teamstats.csv | This is our second data table, Team Stats
4. schedule.csv | This is the current year's NHL schedule
    /models
    5. actualanalytics.csv | Derived scoring model based on 5on5 actual stats
    6. expectedanalytics.csv | Derived scoring model based on 5on5 exp. stats
    7. teamstats.csv | "Expected" statistics provided from the dataset

Statistics
8. poissontable.csv | Blank table I created that will be populated with the likelihood of each outcome for each matchup

/Archive
These are all initial iterations and work of me developing "main.py"


- - - Details - - -
This scoring model was taught to me by Action Backers, a sports analytics platform; with the intention of using publicly available data to predict the likelihood of outcomes for Hockey matches.  Only the model was taught on google sheets, and required lots of time consuming data entry.

The model uses the advanced metric, Expected Goals per-game to give each team an Attack Strength (Exp. Goals For) and Defensive Strength (Exp. Goals Against) Scores.  This is calculated by dividing each team's expected goals (for or against respectively) and dividing it by the (for or against respectively) league average.  This will show you how each team fares compared to the middle of the road teams; and it will also give you how many goals each team typically scores or allows, when multiplying it by the league average.  (Sorry if this is confusing, just stick with me for a minute)
Example:
Boston Bruins - (xgF) expected goals for: 3.78/game  |  (xGA) expected goals against: 2.13/game
This means that the Bruins are expected to score 3.78 goals per game and allow 2.13 goals per game.  If we divide the bruins xGF by the league's average xGF (3.2), we get the Bruin's Attack Strength: 1.18.  If we do the same with xGA, we get the Bruin's Defensive Strength: (2.13 / 3.05) = 0.698; meaning that the bruins on average score 18% more points and allow 30% less points than the typical team.  Meaning that the Bruins are a great Hockey team (Currently the best in the league)

We are going to use the provided expected goals metric from the team stats dataset, and we will calculate expected goals and actual goals for/against from the 5on5 advanced dataset, and the number of games played from the team stats dataset.  Calculate attack/defensive strengths for each segmentation; and then we will aggregate the scores afterwards.
    ! note: I plan to write a script(s) that will run my program through the entire NHL schedule of games that have already been played this year; making predictions for each game and at the end, calculating the error.  The difference between the actual outcome and the predicted outcomes.  I would like it to perform this test numerous times, adjusting the weights of each scoring model to find the combination with the greatest accuracy.

What I want to do is make the scoring predictions for the games that occur today, so I will use the schedule.csv file to determine which games are being played today, and who is playing in them

To calculate each team's score, multiply attack strength (how many goals above/below average you score per game) by the opponent's defensive strength (how many goals above/below average the opponent allows per game) by the league average goals for per game (how many goals each team scores per game).  Do this with each of the three models for each team and aggregate the team's scores.

Once we have an Expected outcome for each matchup, we can use a poisson distribution to predict the likelihood of each outcome in an NHL game, where regular time for the game ends with both teams scoring 0 points, and each combination up to 10 points for both teams.  The poisson distribution takes the team's expected score and says, if you'd typically score this many points; what is the likelihood that you score [as many points as the current iteration has this team scoring]?  
At each iteration (each predicted outcome, i.e. 3-1, 0-1, 9-9) we take that likelihood of occurence and we add it to the winning team's chance of victory.  So if the score is 3-1 meaning that the Away team won, and there's a 3% chance of this outcome happening.  We add to the away team's chance of winning by 3%; and after completing the 100 iterations we have each team's % chance of victory.  If the score was 1-3, the Home team won and we would add the chance to their likelihood.  If the score is a tie, i.e. 3-3; the game will go to a shootout and each team has an equal opportunity at winning; so each team will get 50% of the chance of victory from that outcome.  So if there is a 3% chance that each team will score 4 points, we add 1.5% to each team's chance of victory before moving onto the next iteration

Next, we will use the % chance of victory to determine who is the favorite/underdog and in turn, the odds for each team.  Then ultimately predictions on which team's lack or contain value.
You can lookup (or see in my code) the formulas for converting % chance of victory to american odds or decimal odds; depending on which you use.  I use American odds, so that is what I am converting to, where the favorite has greater than a 50% chance of victory and their odds are negative indicating that if you were to bet $10, you will win some amount less than $10; and the opposite is true for the underdog.

We will store these american odds as our predictions for the game

Next step is to send a request The Odds API, parse the response, and return odds from the book of your choice, to be compared with our predicted odds.  Save these to the predictions database and we are ready to compare

Finally, look through each matchup in today's games and if the price provided by your book is better than the predicted price; it means that your model predicts the team to have a better chance of winning than your book thinks; and that there's an edge for you to take.
For example, if your model says that the Philadelphia Flyers have a 50% chance of winning, this is the equivalent of +100 odds, or you bet $10 to win $10.  A fair bet.  But if the book (wrongly) says that the flyers have a 40% chance of winning (~ +200), you would bet $10 to win $20.  If you were flipping a coin with someone (50% likelihood of tails/heads) and you win $20 for each heads, but only pay $10 for each tails.  Wouldn't you play that game forever?

So the key here is that the model is predicting outcomes and expected scores.  But it is not exactly saying that a team will win.  It is making recomendations based on value.  If a team has a 25% chance of victory, but is wrongly priced at 10% chance of victory; this would be incredible value.  There's a much much better chance of something happening, than the pricemakers believe.  But it does not mean that it is likely to happen.  There is still only a 25% chance of this happening, which is low.  The idea is to find edges, misprices in the market day after day, which is part of the reason we're using NHL.  It's a predictable sport, we've got great metrics to use to build the model, it's low scoring, the outcome is simple, it's just great for our purpose. 


- - - Instructions - - -
When you run main.py you'll want to run, 
- Calculate Predictions, and then Pull Vegas Odds.  After this you can click Display Today's Picks and each of today's picks that contain value will appear in the box on the right, as-well as the size of the price discrepancy (Larger is better).
- Display All of Today's Data is not currently available as I need a more efficient way to display a table of data in my GUI; and I currently have a number of other priorities that are more important.  If you want to see it, you can go in the /Archive directory and go to run.ipynb.  Look for the cell that has a filter for today's date, opens the predictions database and displays the dataframe with filter applied.  You can also just open the csv file with Excel or Numbers and look at the rows that contain today's date
- Update Models:  Download the excel copy of each table from pro-hockey-reference, delete the first row, add the column header "Team" in column B.  Save each dataset in the update folder, as a csv file named, "analytics.csv" or "teamstats.csv" depending on which.  Run the update models button
- Delete Today's Picks:  If you want to re-run today's predictions for whatever reason, this will delete any rows from your predictions database whose date is today