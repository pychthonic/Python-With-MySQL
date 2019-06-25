# Python-With-MySQL

This program first connects to a mysql server. The user inputs a
list of cities, and it uses http requests to find the driving
distance of each city to all the other cities input by the user,
creates a table in the mysql database for all this information,
prints it to the screen, deletes the database, and exits.


Here is a screenshot of it running. The user inputs 6 cities,
4 of which are pretty tiny, and the program uses the Python 
requests package and a map site called www.travelmath.com to 
compute the distances between each individual city and all the 
other cities.


![alt text](https://raw.githubusercontent.com/stephen-wolfe/Python-With-MySQL/master/screenshot_cities.png)
