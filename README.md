# bnpp

 ## N.B.: Dash/plotly saves png files to convert to bmp perform on bash shell:
 ```$ for file in *.png; do convert "$file" "${file%.png}".bmp; done``` 
 I chose NOT to send bmp files as those are more than 10x times bigger than png counterparts
 
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
 - Click on any Scatter plot dots to change the bottom timeseries graph on each person (only works for sends for now)
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
 - The lower timeseries only does sends: Not particularly interested in adding receives
 - Too many global variable (not sure how to encapsulate it - as that would require knowing more than examples
 - Error occurs at 1st start. Know what it is but goes away afterward
 - The Scatter plot is monchrome & unpretty - Should have varied the dot/circle size based on the # send/recieves
 - Needs to understand & play with Dash widgets for placement & control MORE
