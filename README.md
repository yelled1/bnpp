# bnpp
OVERVIEW
========
The main goal is to provide a simple project for Enron email visualization in terms of sends & recieved count

The Objectives are:
 1. Create a csv output file
 2. Create bmp files of times-series graphs
 ### * Please take a look at Images subdirectory 
 #### (especially file ```Images\Dash_scrren_shot_bnpp.bmp```)
 
TO RUN
------
 1. csv output file: 
 - ```pipenv run python summarize_enron.py -i ./enron-event-history-all.csv -o ./enron-email-count.csv ``` 
 takes upto a min but progress is shown on tqdm progress bar
 2. Dash graph generation web-page
 - ```pipenv run python ./dashem.py``` this may take upto 1 min to run 1st time & then pickled data makes it faster
 - Afterwrad open ```http://127.0.0.1:8050/``` on your browser to get Dash up & running
 3. To save bmp files:
 - Change date range using the RangeSlider
 - Select either "Send or Received" using the Dropdown
 - Let the graph update & hover to reveal the camera button: hit to save
 - Repeate above to get different date reanges
 
CAVEAT
======
### Few problem emerged & I bit off much more than I can chew:
 - Should not have tried to use Dash as this was unfamilar to me (1st attempt)
 - Instead I should have wrote things into jupyter notebook, as I am quite familiar with plotly
 - The code quality on the dashem.py is NOT quite upto par, as I was struggling with darn thing to work
 - The idea was to let the user choose his wish & by clicking on the data point the lower bar graph would reflect the time trends, 
 but this did NOT workout as I had no idea how to have multiple outputs
 - However, dropdown & RangeSlider work as expected
 - The Scatter plot is ugly - Should have varied the dot/circle size based on the # send/recieves
 - 2nd lower plot should have been Bar & cumsum of bars as a Line graph with 2nd yaxis (hope to work on later)
 - Needs to understand & play with Dash widgets for placement & control
