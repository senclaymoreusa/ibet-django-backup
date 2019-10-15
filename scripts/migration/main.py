######################################################################################
# This script is NOT part of any django projects and will be run alone by itself.    #
# The whole and only purpose is to migrate all the relevant data from the SQL Server #
# Database (in Taipei) to our Database.                                              #
# Hopefully, we shall need to run it for only ONCE.                                  #
######################################################################################

import pyodbc

# There's really no point for logging, so I will use print everywhere.
print ('Starting the Migration...')

# We do not need to deploy this script anywhere and for now the access is restricted to only our office,
# so there should be no problem to hard code all the credentials.
server = '10.1.10.142'
database = 'MainDB'
username = 'migration'
password = 'Clay1688'

try:
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
except Exception as e:
    print ("Error getting Bonus or User object, Exiting...", e)
    exit(-1)

print ('Successfully connected to the DB:', server, database)












