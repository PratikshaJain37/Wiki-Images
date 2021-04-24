import re
#import pandas as pd

configFile = open("wiki_images_config.txt", "r")
string = configFile.read()

# OUTPUT_FILE = 'Wiki_Images.csv' #add the name of your output file here -- in inverted commas
# USERS = ['Tagooty'] #add the required username(s)-- in inverted commas and seperated by commas 
# MAX_FILES = -1 #add the max files you want to search -- -1 (default) searches all files
# COUNT_ONLY = False #write True to count number of files only, without links

OUTPUT_FILE = re.search(r'OUTPUT_FILE( *)=(( *)\'(.*).csv\'( *)?(,?)( *)?)+', string, re.M|re.I).group()
OUTPUT_FILE = OUTPUT_FILE.replace(" ", "")      #removing whitespaces
OUTPUT_FILE = OUTPUT_FILE.replace("OUTPUT_FILE=", "")       #accessing the .csv file names


USERS = re.search(r'USERS( *)=( *)(\[)(( *)\'(.*)\'( *)?(,?)( *)?)+(\])', string, re.M|re.I).group()
USERS = USERS.replace(" ", "")      #removing whitespaces
USERS = USERS.replace("USERS=", "")       #accessing the usernames


MAX_FILES = re.search(r'MAX_FILES( *)=( *)(-?)(\d)+', string, re.M|re.I).group()
MAX_FILES = MAX_FILES.replace(" ", "")      #removing whitespaces
MAX_FILES = MAX_FILES.replace("MAX_FILES=", "")       #accessing the number of files user wants to search 
MAX_FILES = int(MAX_FILES)      #typecasting into integer 


COUNT_ONLY = re.search(r'COUNT_ONLY( *)=( *)[(True)|(False)]( *)', string, re.M|re.I).group()
COUNT_ONLY = COUNT_ONLY.replace(" ", "")      #removing whitespaces
COUNT_ONLY = COUNT_ONLY.replace("COUNT_ONLY=", "")       #accessing if user wants to count number of files only, without links

print(COUNT_ONLY)