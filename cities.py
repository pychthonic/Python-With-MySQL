import mysql.connector, requests, re, getpass, sys

"""
This program first connects to a mysql server. The user then inputs a list 
of cities, and it uses http requests to find the driving distance of each 
city to all the other cities input by the user, creates a table in the 
mysql database for all this information, prints it to the screen, deletes 
the database, and exits.

Next step is making it object oriented.

"""

def connectToDatabase():
    hostip = input("\nEnter ip of database host, or just hit enter for 127.0.0.1): ")
    if hostip == "":
        hostip = '127.0.0.1'
    username = input("Enter username for {}: ".format(hostip))
    password = getpass.getpass("Enter password for {}: ".format(username))
    try:
        mydb = mysql.connector.connect(
                host = hostip,
                user = username,
                passwd = password,
                )
    except mysql.connector.errors.ProgrammingError:
        print("\nFailed to connect to {}. Exiting.\n".format(hostip))
        sys.exit()
        
    print("\nSuccessfully connected to {}\n".format(hostip))
    return mydb



def getDistance(city1, city2):
    
    city1forlink = city1.replace(" ", "+")
    city2forlink = city2.replace(" ", "+")
    
    link = 'https://www.travelmath.com/drive-distance/from/{}/to/{}'.format(city1forlink, city2forlink)

    ua = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'}


    response = requests.get(link, headers=ua)               
    try:
        searchstring = "The total driving distance from {} to {} is <strong>(.*)miles".format(city1, city2)
        miles = re.search(searchstring, response.text).group(1)
        miles = re.search('(.+?) ', miles).group(1)
    except AttributeError:
        miles = "distance not found"

    return miles


mydb = connectToDatabase()

citiesList = []

statesList = ['AK', 'AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', \
        'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', \
        'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', \
        'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

statesString = """Alabama - AL\tAlaska - AK\tArizona - AZ\tArkansas - AR\tCalifornia - CA\tColorado - CO\t
Connecticut - CT\tDelaware - DE\tFlorida - FL\tGeorgia - GA\tHawaii - HI\tIdaho - ID\tIllinois - IL\t
Indiana - IN\tIowa - IA\tKansas - KS\tKentucky - KY\tLouisiana - LA\tMaine - ME\tMaryland - MD\t
Massachusetts - MA\tMichigan - MI\tMinnesota - MN\tMississippi - MS\tMissouri - MO\tMontana - MT\t
Nebraska - NE\tNevada - NV\tNew Hampshire - NH\tNew Jersey - NJ\tNew Mexico - NM\tNew York - NY\t
North Carolina - NC\tNorth Dakota - ND\tOhio - OH\tOklahoma - OK\tOregon - OR\tPennsylvania - PA\t
Rhode Island - RI\tSouth Carolina - SC\tSouth Dakota - SD\tTennessee - TN\tTexas - TX\tUtah - UT\t
Vermont - VT\tVirginia - VA\tWashington - WA\tWest Virginia - WV\tWisconsin - WI\tWyoming - WY\n\n"""


def printStates():
    print("\nList of 50 states with their abbreviations:\n\n" + statesString)

while True:
    newcity = input("\nEnter a city, or just enter when finished: ").title()
    if newcity:
        newstate = input("\nWhat state is {} in? (format: PA for Pennsylvania): ".format(newcity))
        while newstate.upper() not in statesList:
            if newstate != 'help' and newstate != 'h':
                print("\nBad input. Enter 'help' or 'h' to display list of states with their two \
                        letter abbreviations.")
            newstate = input("\nPlease enter two letters of {}'s state: ".format(newcity))
            if newstate == "help" or newstate == "h":
                printStates()
        newcity += ", {}".format(newstate.upper())
        if newcity in citiesList:
            print("You already entered {}\n".format(newcity))
            continue
        citiesList.append(newcity)
    
    if newcity == "":
        break

print('\n\nCreating database...\n\n')

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS citiesdata;")
mycursor.execute("USE citiesdata;")

mycursor.execute("DROP TABLE IF EXISTS citiesDistance;")

tableCreationCommand = "CREATE TABLE citiesDistance (cityName VARCHAR(255), "

recordCreationCommand = "INSERT INTO citiesDistance (cityName, "

recordCreationSuffix = ") VALUES (%s, "

for city in citiesList:
    tableCreationCommand += "distanceTo" + city.replace(",", "").replace(" ", "") + " INT(10), "
    
    recordCreationCommand += "distanceTo" + city.replace(",", "").replace(" ", "") + ", "
    recordCreationSuffix += "%s, "

tableCreationCommand = tableCreationCommand[:-2]
tableCreationCommand += ");"

recordCreationCommand = recordCreationCommand[:-2] + recordCreationSuffix[:-2] + ");"

mycursor.execute(tableCreationCommand)

for city1 in citiesList:
    distanceDict = {}

    for city2 in citiesList:
        dist = getDistance(city1, city2)
        distanceDict["distanceTo{}".format(city2.replace(',', '').replace(' ', ''))] = \
                dist.replace(",", "")

    record = (city1, )
    for key, value in distanceDict.items():
        nextItem = (value, )
        record += nextItem
    mycursor.execute(recordCreationCommand, record)

    mydb.commit()


mycursor.execute("SELECT * FROM citiesDistance")
result = mycursor.fetchall()

print()

tableColumnLabelString = "\n\nCity ".ljust(24)
tableColumnLabelLine = "----".ljust(22)

for city in citiesList:
    tableColumnLabelString += ("to " + city).ljust(23)
    tableColumnLabelLine += ("-" * len("to " + city)).ljust(23)

print(tableColumnLabelString)
print(tableColumnLabelLine)

for row in result:
    for item in row:
        if item == row[0]:
            print(item.ljust(22), end="")
        else:    
            print(str(item).ljust(23), end="")
    print()

mycursor.execute("DROP DATABASE citiesdata")

databaseDeleted = True

mycursor.execute("SHOW DATABASES")

for db in mycursor:
    if db[0] == 'citiesdata':
        databaseDeleted = False
        break
        
if databaseDeleted == True:
    print("\nDatabase deleted.\n\n")
else:
    print("\nWarning: Database not deleted.\n\n")

mydb.close()

