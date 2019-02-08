import re
import getpass
import sys

import mysql.connector
import requests


class CitySearch:
    """This program first connects to a mysql server. The user inputs a
    list of cities, and it uses http requests to find the driving 
    distance of each city to all the other cities input by the user,
    creates a table in the mysql database for all this information, 
    prints it to the screen, deletes the database, and exits.
    """
    states_list = ['AK', 'AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL',
            'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
            'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
            'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
            'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI',
            'WY']

    states_string = """Alabama - AL\tAlaska - AK\tArizona - AZ\t
    Arkansas - AR\tCalifornia - CA\tColorado - CO\tConnecticut - CT\t
    Delaware - DE\tFlorida - FL\tGeorgia - GA\tHawaii - HI\tIdaho - ID\t
    Illinois - IL\tIndiana - IN\tIowa - IA\tKansas - KS\tKentucky - KY\t
    Louisiana - LA\tMaine - ME\tMaryland - MD\tMassachusetts - MA\t
    Michigan - MI\tMinnesota - MN\tMississippi - MS\tMissouri - MO\t
    Montana - MT\tNebraska - NE\tNevada - NV\tNew Hampshire - NH\t
    New Jersey - NJ\tNew Mexico - NM\tNew York - NY\t
    North Carolina - NC\tNorth Dakota - ND\tOhio - OH\tOklahoma - OK\t
    Oregon - OR\tPennsylvania - PA\tRhode Island - RI\t
    South Carolina - SC\tSouth Dakota - SD\tTennessee - TN\tTexas - TX\t
    Utah - UT\tVermont - VT\tVirginia - VA\tWashington - WA\t
    West Virginia - WV\tWisconsin - WI\tWyoming - WY\n\n"""

    def __init__(self):
        """Connect to the MySQL database. Create a list of cities.
        Connect to MySQL server. Create a database on the MySQL server
        for the list of cities. Print out the database. Delete the
        database and exit the server.
        """
        self.cities_list = []
        self.create_city_list()
        self.connect_to_MySQL_server()
        self.create_database()
        self.print_database_table()
        self.delete_database_and_exit()

    def connect_to_MySQL_server(self):
        """Take MySQL server ip address, username and password entered 
        by user, and connect.
        """
        self.host_ip = input("\nEnter ip of database host, or just hit enter "
                        "for 127.0.0.1): ")
        if self.host_ip == "":
            self.host_ip = '127.0.0.1'
        self.username = input("Enter username for {}: ".format(self.host_ip))
        self.password = getpass.getpass(
            "Enter password for {}: ".format(self.username))
        try:
            self.my_db = mysql.connector.connect(
                    host = self.host_ip,
                    user = self.username,
                    passwd = self.password,
                    )
        except mysql.connector.errors.ProgrammingError:
            print("\nFailed to connect to {}. Exiting.\n".format(self.host_ip))
            sys.exit()

        print("\nSuccessfully connected to {}\n".format(self.host_ip))

    def get_distance(self, city1, city2):
        """Take two cities, and use requests module to find driving
        distance between them.
        """
        city1_for_link = city1.replace(" ", "+")
        city2_for_link = city2.replace(" ", "+")

        link = ("https://www.travelmath.com"
            "/drive-distance/from/{}/to/{}".format(
                                            city1_for_link, city2_for_link))

        ua = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) '
                                                'Gecko/20100101 Firefox/65.0'}


        response = requests.get(link, headers=ua)
        try:
            search_string = (
                "The total driving distance "
                "from {} to {} is <strong>(.*)miles".format(city1, city2))
            miles = re.search(search_string, response.text).group(1)
            miles = re.search('(.+?) ', miles).group(1)
        except AttributeError:
            miles = "distance not found"

        return miles

    def print_states(self):
        """This method is called if the user asks to see a list of the
        50 states and their abbreviations.
        """
        print(
            "\nList of 50 states with their abbreviations:\n\n" 
            + self.states_string)

    def create_city_list(self):
        """Allow user to input as many cities as they want and put them 
        in self.cities_list[].
        """
        while True:
            new_city = input(
                "\nEnter a city, or just enter when finished: ").title()
            if new_city:
                new_state = input(
                    "\nWhat state is {} in? "
                    "(format: PA for Pennsylvania): ".format(new_city))
                while new_state.upper() not in self.states_list:
                    if new_state != 'help' and new_state != 'h':
                        print(
                            "\nBad input. Enter 'help' or 'h' to display list"
                            " of states with their two letter abbreviations.")
                    new_state = input(
                        "\nPlease enter two letters "
                        "of {}'s state: ".format(new_city))
                    if new_state == "help" or new_state == "h":
                        self.print_states()
                new_city += ", {}".format(new_state.upper())
                if new_city in self.cities_list:
                    print("You already entered {}\n".format(new_city))
                    continue
                self.cities_list.append(new_city)
            else:
                break

    def create_database(self):
        """Creates a MySQL database and table. Inside the table, each 
        city gets its own record. The fields are the distance from
        that city to each of the other cities entered by the user.
        For example, if the user entered New York, NY, Santa Cruz, CA,
        and Detroit, MI, the first row would belong to New York and the 
        fields would be distanceToSantaCruzCA and distanceToDetroitMI.
        The get_distance() method is used to find the distance between
        any two given cities.
        """
        print('\n\nCreating database...\n\n')
        self.my_cursor = self.my_db.cursor()
        self.my_cursor.execute("CREATE DATABASE IF NOT EXISTS citiesdata;")
        self.my_cursor.execute("USE citiesdata;")
        self.my_cursor.execute("DROP TABLE IF EXISTS citiesDistance;")

        table_creation_command = (
            "CREATE TABLE citiesDistance (cityName VARCHAR(255), ")
        record_creation_command = (
            "INSERT INTO citiesDistance (cityName, ")
        record_creation_suffix = ") VALUES (%s, "

        for city in self.cities_list:
            table_creation_command += (
                                    "distanceTo"
                                    + city.replace(",", "").replace(" ", "")
                                    + " INT(10), ")
            record_creation_command += (
                                    "distanceTo"
                                    + city.replace(",", "").replace(" ", "")
                                    + ", ")
            record_creation_suffix += "%s, "

        table_creation_command = table_creation_command[:-2]
        table_creation_command += ");"
        record_creation_command = (
                                record_creation_command[:-2]
                                + record_creation_suffix[:-2]
                                + ");")

        self.my_cursor.execute(table_creation_command)

        for city1 in self.cities_list:
            distance_dict = {}
            for city2 in self.cities_list:
                dist = self.get_distance(city1, city2)
                distance_dict["distanceTo{}".format(
                                        city2.replace(',', '').replace(' ', '')
                                        )] = dist.replace(",", "")
            record = (city1,)
            for key, value in distance_dict.items():
                next_item = (value,)
                record += next_item
            self.my_cursor.execute(record_creation_command, record)
            self.my_db.commit()

    def print_database_table(self):
        """This method prints the database created in the 
        create_database() method to the screen, formatted to make it
        easy on the eyes.
        """
        self.my_cursor.execute("SELECT * FROM citiesDistance")
        result = self.my_cursor.fetchall()

        table_column_label_string = "\n\nCity ".ljust(24)
        table_column_label_line = "----".ljust(22)

        for city in self.cities_list:
            table_column_label_string += ("to " + city).ljust(23)
            table_column_label_line += ("-" * len("to " + city)).ljust(23)

        print("\n" + table_column_label_string)
        print(table_column_label_line)

        for row in result:
            for item in row:
                if item == row[0]:
                    print(item.ljust(22), end="")
                else:    
                    print(str(item).ljust(23), end="")
            print()

    def delete_database_and_exit(self):
        """This method deletes the database created in the
        create_database() method, and checks to make sure
        it was deleted. It then exits the connection with
        the MySQL server.
        """
        self.my_cursor.execute("DROP DATABASE citiesdata")
        self.database_deleted = True
        self.my_cursor.execute("SHOW DATABASES")
        for db in self.my_cursor:
            if db[0] == 'citiesdata':
                self.database_deleted = False
                break
        if self.database_deleted == True:
            print("\nDatabase deleted.\n\n")
        else:
            print("\nWarning: Database not deleted.\n\n")
        self.my_db.close()


if __name__ == '__main__':
    search = CitySearch()
