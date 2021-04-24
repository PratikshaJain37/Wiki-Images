"""
Wiki Images - Main script
Version 1.2.2
Authors : Pratiksha Jain, Deepali Singh

"""
#---------------------------------------------#
'''
For running this script:

The script is mainly Python3.7 compliant.

Library versions it runs with - 
a. requests 2.24.0
(https://pypi.org/project/requests/)
b. beautifulsoup4 4.9.3
(https://pypi.org/project/beautifulsoup4/)
c. pandas 1.1.3
(https://pypi.org/project/pandas/)
d. tqdm 4.54.0
(https://pypi.org/project/tqdm/)
e. time 
GNU time 1.7

For running the script (inside a virtual environment):
(With reference from https://docs.python.org/3/tutorial/venv.html)

1. Setting up the virtual environment in the folder
$ python3 -m venv images_venv

2. Activating the virtual environment 
In Windows:
$ images_venv/Scripts/activate.bat
In Linux/Unix:
$ source ./venv/bin/activate
(If you use the csh or fish shells, the alternate is activate.csh and activate.fish)

3. Installing the required libraries
    $ pip3 install requests beautifulsoup4 pandas getopt sys tqdm

4. Running the script
    $ python3 wiki_images.py

A new csv file, with the name 'Wiki_Images.csv' will appear, which has the required output.

(For running outside a virtual environment, step 1 can be eliminated, but dependencies may have to be updated later on.)

'''
#---------------------------------------------#

# Libraries Used
import requests
from bs4 import BeautifulSoup
import pandas as pd
import getopt
import sys
from tqdm import tqdm
import time

#---------------------------------------------#

# Initializing counters for Summary Info
counter_time = time.time() # To check time taken
counter_qualityImage = 0 # Number of quality images
counter_featuredImage = 0 # Number of featured images
counter_valuedImage = 0 # Number of valued images
counter_dataFiltered = 0 # Number of media featured on other wikis
counter_UsageOnWikis = 0 # Number of pages which media has been featured in

#---------------------------------------------#

# Defining System Variables

RUN = True  # For running the code
HELP_MENU = False  #For help menu options
OUTPUT_FILE = 'Wiki_Images.csv' # Output of program
QUIET_MODE = False  # If no updates to be given while processing
USER = 'Tagooty' # For user name
MAX_FILES = -1  # Max files by user to search
COUNT_ONLY = False # Count number of files only, without links
SUMMARY_INFO = True
VERSION = 'v1.2.2'

HELP_OPTIONS = '''
Wiki Images
v1.2
Authors: Pratiksha Jain, Deepali Singh
-h, --help : Displays Help Menu
-o, --outputfile <filename> : In case output is to be made on different file. Default is "Wiki_Images.csv"
-q, --quietmode : Suppresses output on terminal
-u, --user : Specifies user. Default is "Tagooty"
-m, --maxfiles : Specifies maximum number of images to filter through
-c, --countonly : If only image and number of wikis featured in is to be displayed
-v, --version : Version number
'''

#---------------------------------------------#

# For processing Command Line Arguments
options, remainder = getopt.gnu_getopt(sys.argv[1:], 'ho:qu:m:csv', ['help','outputfile=',
'quietmode',
'user=',
'maxfiles=',
'countonly',
'version',    
])

for opt, arg in options:
    if opt in ('-h'):
        print(HELP_OPTIONS)
        RUN = False
    elif opt in ('-o', '--outputfile'):
        OUTPUT_FILE = arg + '.csv'
    elif opt in ('-q', '--quietmode'):
        QUIET_MODE = True
    elif opt in ('-u', '--user'):
        USER = arg
    elif opt in ('-m', '--maxfiles'):
        MAX_FILES = arg
    elif opt in ('-c', '--countonly'):
        COUNT_ONLY = True
    elif opt in ('-v','--version'):
        print('Wiki Images\nVersion 1.2.2\nPratiksha Jain and Deepali Singh')
        RUN = False

#---------------------------------------------#

# Defining classes for database

# Attributes of Wiki Image class corresponds to the columns in the main table on - attributes can be added/removed easily
# https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=Tagooty
# The is_quality)image and is_featured_image attributes have been initialised with None (blank) values - only True if true
# The usage_on_wikis attribute contains a list of pages where it has been used on other wikis

class wiki_image():
    timestamp = False 
    name = False
    path = False
    is_quality_image = None
    is_featured_image = None
    is_valued_image = None
    usage_on_wikis = []  # List of wiki_pages

# Attributes of each wiki_page correspond to the name and link of each of the required pages. 
class wiki_page():
    name = False
    link = False

#---------------------------------------------#

# STEP 1: Extracting data from Main Wiki and storing in a database

def parseData(USER='Tagooty', baseurl='https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=', url=False):
    if not url: # Defining the URL
        URL = baseurl + USER
    else:
        URL = url

    page = requests.get(URL) # Getting the content
    soup = BeautifulSoup(page.content, 'html.parser') # For parsing the content in the mentioned URL
    return soup

def extractData(soup, MAX_FILES):
    
    data = [] # Initialising empty list for storing wiki_image elements
    table = soup.find("table", attrs={"class": 'mw-datatable listfiles'}) # Finding required table

    for row in table.tbody.find_all("tr"): # Iterating over all the row elements in table
        temp = wiki_image() # Creating an instance of a wiki_image
        column = row.find("td", attrs={"class": "TablePager_col_img_timestamp"}) 
        temp.timestamp = column.text # For finding its timestamp 

        for link in row.find_all("a", href=True): # Finding links ('a' tags) in each row
            if link["href"].startswith("/wiki/File:"): # Finding the link which starts with 'File'
                link["title"] = link["title"].replace("File:", "")
                link["title"] = link["title"].replace(".jpg", "") # Cleaning name 
                temp.name = link["title"]
                temp.path = "https://commons.wikimedia.org" + link["href"]
                break    
        data.append(temp) # Adding the wiki_image instance to the database
 
    if MAX_FILES == -1: # Condition for max_files to go through
        return data
    else:
        return data[:min(MAX_FILES, len(data))]

#---------------------------------------------#

# STEP 2:
#2.1 visiting the page for each image (object)
#2.2 accessing section "File usage on other wikis" (if it exists)
#2.3 appending name and link of 'wiki pages' in usage_in_wikis (excluding "Talk:" and "User:")
#2.4 checking if it is a 'Quality Image' or/and 'Featured Image'


def collectData(obj):
    # global variables-counters
    global counter_featuredImage, counter_qualityImage, counter_valuedImage, counter_UsageOnWikis

    soup_images = parseData(url=obj.path) # Visiting page for each image (object)
    heading = soup_images.find("div", attrs={"id": 'mw-imagepage-section-globalusage'})  # Accessing section "File usage on other wikis" (if it exists)
    obj.usage_on_wikis = [] # Initialising empty variable
    bool_dataFiltered = False  # For counter for amount of data got after filtering

    if heading is not None:  
        for index, link in enumerate(heading.find_all("a", href=True)): # Finding 'wiki page' names and links 
            if 'USER:' in link["href"] or 'User:' in link["href"]  or 'Talk:' in link["href"]:   # Filtering out "USER:" and "Talk:"
                continue
            else:    
                temp_images = wiki_page()
                temp_images.name = link.text  # Saving names of each wiki page correspoding the respective image (object) in class wiki_pages()
                temp_images.link = link["href"]  # Saving links of each wiki page correspoding the respective image (object) in class wiki_pages() 
                obj.usage_on_wikis.append(temp_images)  # Appending the wiki_page() database in the list usage_in_wikis
                bool_dataFiltered = True      
    
    counter_UsageOnWikis += len(obj.usage_on_wikis)

    if 'This image has been assessed using the Quality image guidelines and is considered a Quality image.' in soup_images.text:  # Checking if it is a 'Quality Image'
        obj.is_quality_image = True   
        counter_qualityImage += 1
    
    if 'This is a featured picture on' in soup_images.text:  # Checking if it is a 'Featured Image'  
        obj.is_featured_image = True 
        counter_featuredImage += 1

    if 'This image has been assessed under the valued image criteria and is considered the most valued image on Commons' in soup_images.text:  # Checking if it is a 'Valued Image'  
        obj.is_valued_image = True 
        counter_valuedImage += 1

    return obj, bool_dataFiltered

#---------------------------------------------#

# Step 3: Displaying it in a .csv file

def outputData(data, COUNT_ONLY):
    if COUNT_ONLY == True: # If only count of wikis featured in is required
        headers = [
            'Name',
            'Number of Wikis Featured In',
            'Quality Image',
            'Featured Image',
        ]

        df = pd.DataFrame(columns=headers) # Initialisng an empty dataframe to store elements in data

        for obj in data: # Storing all the required links and infomation in the dataframe   
            df = df.append({
                            'Name' : obj.name,
                            'Number of Wikis Featured In' : len(obj.usage_on_wikis),
                            'Quality Image' : obj.is_quality_image,
                            'Featured Image' : obj.is_featured_image,
                        }, ignore_index=True) 

    else:
        headers = [
        'Name', 
        #'Path',
        #'Time Stamp',
        'Featured In - Page',
        'Featured In - Link',
        'Quality Image',
        'Featured Image',
        'Valued Image',
        ]
        
        df = pd.DataFrame(columns=headers) # Initialisng an empty dataframe to store elements in data

        for obj in data:  # Storing all the required links and infomation in the dataframe - only if they have been used on other wikis
            if len(obj.usage_on_wikis) == 0:
                continue
            else:
                for index, page in enumerate(obj.usage_on_wikis):  # Uncomment if-else statement in the loop -- in case you want multiple usage_on_wikis links to appear on separate lines (with white spaces in Featured-In column)
                    # if index == 0:
                        df = df.append({
                            'Name' : obj.name,
                            #'Path' : obj.path,
                            #'Time Stamp' : obj.timestamp,
                            'Quality Image' : obj.is_quality_image,
                            'Featured Image' : obj.is_featured_image,
                            'Valued Image' : obj.is_valued_image,
                            "Featured In - Page" : page.name,
                            'Featured In - Link': page.link
                        }, ignore_index=True) 
                    # else:
                    #     df = df.append({
                    #         "Featured In - Page" : page.name,
                    #         "Featured In - Link": page.link
                    
                    #     }, ignore_index=True)
    return df
        
#---------------------------------------------#

# Driver Code

if RUN == False: # Main check
    sys.exit()

if QUIET_MODE == True: # If no output is to be given in terminal
    soup = parseData(USER=USER)
    data = extractData(soup, MAX_FILES)
    
    for obj in data: # Iterating over data
        obj_filtered, bool_dataFiltered = collectData(obj)
        obj = obj_filtered
    
    df = outputData(data, COUNT_ONLY)

else:   # progress bar – QUIET_MODE == True (default)
    soup = parseData(USER=USER)
    data = extractData(soup, MAX_FILES)
    print("\nData parsed and extracted.\n")
    for obj, perc in zip(data, tqdm (range(len(data)), initial=1, desc="Filtering data...")): # Iterating over data, and showing progress bar
        obj_filtered, bool_dataFiltered = collectData(obj)
        obj = obj_filtered
        if bool_dataFiltered == True: # Condition - if it featured in other wikis
            counter_dataFiltered += 1
    print("Filering complete.")

    df = outputData(data, COUNT_ONLY) # Getting output as pandas dataframe
    
df.to_csv(OUTPUT_FILE, index=False, header=True) # Giving output in csv file
print("\nExporting Complete. The csv file can be found as %s in your folder."%(OUTPUT_FILE))

print("\nSUMMARY INFO:")      #summary info
print("*Total media found --", len(data))
print("*Number of media used in other wikis --", str(counter_dataFiltered) + " (" + str(round(counter_dataFiltered/len(data)*100,2))+"%)")
print("*Total pages which have the media featured on them -- ", str(counter_UsageOnWikis))
print("*Total number of Quality Images -- ", counter_qualityImage)
print("*Total number of Featured Images -- ", counter_featuredImage)
print("*Total number of Valued Images -- ", counter_valuedImage)
print ("\n--- %s seconds taken ---" % round((time.time() - counter_time),2))

#---------------------------------------------#