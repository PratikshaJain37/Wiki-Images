"""
Wiki Images - Main script
Version 1.3.4
Authors : Pratiksha Jain, Deepali Singh

Change Log: 27/3/2010 Chanchla K & TAG
            Changed single USER to list users
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
import concurrent.futures
import threading

#---------------------------------------------#

# Initializing counters for Summary Info
counter_time = time.time() # To check time taken

#---------------------------------------------#

# Defining System Variables

from config import * #importing from config file

RUN = True  # For running the code
HELP_MENU = False  #For help menu options
VERSION = 'v1.3.4'
summary_info = True
quiet_mode = False  # If no updates to be given while processing

HELP_OPTIONS = '''
Wiki Images
v1.3.2
Authors: Pratiksha Jain, Deepali Singh
-h, --help : Displays Help Menu
-o, --outputfile <filename> : In case output is to be made on different file. Default is "Wiki_Images.csv"
-q, --quietmode : Suppresses output on terminal
-u, --user : comma-separated list of users. Default is "Tagooty"
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
        output_file = arg + '.csv'
    elif opt in ('-q', '--quietmode'):
        quiet_mode = True
    elif opt in ('-u', '--user'):
        users = arg
        if isinstance(users, str):
            users = users.split(", ")
    elif opt in ('-m', '--maxfiles'):
        max_files = arg
    elif opt in ('-c', '--countonly'):
        count_only = True
    elif opt in ('-v','--version'):
        print('Wiki Images\nVersion 1.3.2\nPratiksha Jain and Deepali Singh')
        RUN = False

#---------------------------------------------#

# Defining classes for database

# Attributes of Wiki Image class corresponds to the columns in the main table on - attributes can be added/removed easily
# For reference: https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=Tagooty
# The is_quality)image and is_featured_image attributes have been initialised with None (blank) values - only True if true
# The usage_on_wikis attribute contains a list of pages where it has been used on other wikis
# The user attribute specifies which user owns that image

class wiki_image():
    timestamp = False 
    name = False
    path = False
    is_quality_image = None
    is_featured_image = None
    is_valued_image = None
    user = None
    is_used_in_other_wikis = False # For counter for amount of data got after filtering
    usage_on_wikis = []  # List of wiki_pages
    
# Attributes of each wiki_page correspond to the name and link of each of the required pages. 
class wiki_page():
    name = False
    link = False

class list_wiki(list):

    thread_update_counter = 0
    lock = threading.Lock()

    def query(self, parameter, value):
        queried_list = []
        for item in self:
            if getattr(item, parameter) == value:
                queried_list.append(item)
        return queried_list

    def update(self, obj, index):
        obj_filtered = collectData(obj)
        self[index] = obj_filtered
        
        with self.lock:
            local_copy = self.thread_update_counter
            local_copy += 1
            self.thread_update_counter = local_copy
        
        print_log('Filtering %d of %d: (%s)'%(self.thread_update_counter, len(self), obj.name[:20]), end='\r')

        ## Threading check ##
        #print_log('Filtering %d of %d: (%d: %s)'%(self.thread_update_counter, len(self), index, obj.name[:20]), end='\r')
        
        
    
#---------------------------------------------#

# STEP 1: Extracting data from Main Wiki and storing in a database
def parseData(USER="", baseurl='https://commons.wikimedia.org/wiki/Special:ListFiles?limit=9999999&user=', url=False):
    if not url: # Defining the URL
        URL = baseurl + USER
    else:
        URL = url
    page = requests.get(URL) # Getting the content
    soup = BeautifulSoup(page.content, 'html.parser') # For parsing the content in the mentioned URL
    return soup

def extractData(soup, max_files, user):
    data = list_wiki() # Initialising empty list for storing wiki_image elements
    table = soup.find("table", attrs={"class": 'mw-datatable listfiles'}) # Finding required table

    for row in table.tbody.find_all("tr"): # Iterating over all the row elements in table
        temp = wiki_image() # Creating an instance of a wiki_image
        column = row.find("td", attrs={"class": "TablePager_col_img_timestamp"}) 
        temp.timestamp = column.text # For finding its timestamp 

        for link in row.find_all("a", href=True): # Finding links ('a' tags) in each row
            if link["href"].startswith("/wiki/File:"): # Finding the link which starts with 'File'
                link["title"] = link["title"].replace("File:", "")
                link["title"] = link["title"].replace(".jpg", "") # Cleaning name 
                temp.user = user
                temp.name = link["title"]
                temp.path = "https://commons.wikimedia.org" + link["href"]
                break    
        data.append(temp) # Adding the wiki_image instance to the database)
    if max_files == -1: # Condition for max_files to go through
        return data
    else:
        return data[:min(max_files, len(data))]

#---------------------------------------------#

# STEP 2:
#2.1 visiting the page for each image (object)
#2.2 accessing section "File usage on other wikis" (if it exists)
#2.3 appending name and link of 'wiki pages' in usage_in_wikis (excluding "Talk:" and "User:")
#2.4 checking if it is a 'Quality Image' or/and 'Featured Image'


def collectData(obj):

    soup_images = parseData(url=obj.path) # Visiting page for each image (object)
    heading = soup_images.find("div", attrs={"id": 'mw-imagepage-section-globalusage'})  # Accessing section "File usage on other wikis" (if it exists)
    obj.usage_on_wikis = [] # Initialising empty variable 

    if heading is not None:  
        for index, link in enumerate(heading.find_all("a", href=True)): # Finding 'wiki page' names and links 
            if 'USER:' in link["href"] or 'User:' in link["href"]  or 'Talk:' in link["href"]:   # Filtering out "USER:" and "Talk:"
                continue
            else:    
                temp_images = wiki_page()
                temp_images.name = link.text  # Saving names of each wiki page correspoding the respective image (object) in class wiki_pages()
                temp_images.link = link["href"]  # Saving links of each wiki page correspoding the respective image (object) in class wiki_pages() 
                obj.usage_on_wikis.append(temp_images)  # Appending the wiki_page() database in the list usage_in_wikis
                obj.is_used_in_other_wikis = True      

    if 'This image has been assessed using the Quality image guidelines and is considered a Quality image.' in soup_images.text:  # Checking if it is a 'Quality Image'
        obj.is_quality_image = True   
    
    if 'This is a featured picture on' in soup_images.text:  # Checking if it is a 'Featured Image'  
        obj.is_featured_image = True 

    if 'This image has been assessed under the valued image criteria and is considered the most valued image on Commons' in soup_images.text:  # Checking if it is a 'Valued Image'  
        obj.is_valued_image = True 

    return obj

#---------------------------------------------#

# Step 3: Displaying it in a .csv file

def outputData(data, count_only):
    if count_only == True: # If only count of wikis featured in is required
        headers = [
            'User',
            'Name',
            'Number of Wikis Featured In',
            'Quality Image',
            'Featured Image',
            'Valued Image'
        ]

        df = pd.DataFrame(columns=headers) # Initialisng an empty dataframe to store elements in data

        for obj in data: # Storing all the required links and infomation in the dataframe   
            df = df.append({
                            'User' : obj.user,
                            'Name' : obj.name,
                            'Number of Wikis Featured In' : len(obj.usage_on_wikis),
                            'Quality Image' : obj.is_quality_image,
                            'Featured Image' : obj.is_featured_image,
                            'Valued Image' : obj.is_valued_image,
                        }, ignore_index=True) 

    else:
        headers = [
        'User',
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
                            'User': obj.user,
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

def summarizeData(data):
    
    counters = {
    'qualityImage' : 0, # Number of quality images
    'featuredImage' : 0, # Number of featured images
    'valuedImage' : 0, # Number of valued images
    'counter_dataFiltered' : 0, # Number of media featured on other wikis
    'counter_UsageOnWikis' : 0, # Number of pages which media has been featured in
    }

    # Temporary variable for links master list
    temp_usage_on_wikis_list = []

    for obj in data:
        if obj.is_quality_image == True:  
            counters['qualityImage'] += 1
    
        if obj.is_featured_image == True:
            counters['featuredImage'] += 1

        if obj.is_valued_image == True: 
            counters['valuedImage'] += 1
        
        if obj.usage_on_wikis != 0:
            temp_usage_on_wikis_list += [page.link for page in obj.usage_on_wikis]
            
        if obj.is_used_in_other_wikis == True:    
            counters['counter_dataFiltered'] += 1
    
    # Removing duplicates
    counters['counter_UsageOnWikis'] = len(set(temp_usage_on_wikis_list))

    print_log("*Total media found -- %d" %(len(data)))
    print_log("*Number of media used in other wikis -- {} ({}%)".format(counters['counter_dataFiltered'],
    counters['counter_dataFiltered']/len(data)*100))
    print_log("*Total pages which have the media featured on them -- %d"%(counters['counter_UsageOnWikis']))
    print_log("*Total number of Quality Images -- %d"%(counters['qualityImage']))
    print_log("*Total number of Featured Images -- %d"%( counters['featuredImage']))
    print_log("*Total number of Valued Images -- %d"%( counters['valuedImage']))
    print_log("\n")

#---------------------------------------------#

def print_log(message, end='\n'):
    global quiet_mode
    if quiet_mode == False:
        print (message, end=end)

#---------------------------------------------#
# Driver Code

if RUN == False: # Main check
    sys.exit()

data = list_wiki() # Creating empty list

print_log("Parsing and extracting data for: ", end='')
for u in users:
    soup = parseData(u)
    data = list_wiki(data + extractData(soup, max_files, u))
    print_log(u, end='')
print_log("... [Done] \n")


with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    for index, obj in enumerate(data):
        executor.submit(data.update, obj, index)
print_log("\nFiltering [Done]")

df = outputData(data, count_only)
   
print_log("\nExporting...", end='\r')
df.to_csv(output_file, index=False, header=True) # Giving output in csv file
print_log("Exporting [Done]\nThe csv file can be found as %s in your folder."%(output_file))

print("\nSUMMARY INFO: for users", users)
summarizeData(data)
print ("\n--- %s seconds taken ---" % round((time.time() - counter_time),2))
print()

#---------------------------------------------#

# Summary info for each individual user 
# EDIT HERE: if specifics of other parameters (of class wiki_images - narely: timestamp, name, path, is_quality_image, is_featured_image, is_valued_image, user, is_used_in_other_wikis, usage_on_wikis) are wanted - refer to function query under class:list_wiki (defined above) for format

for u in users:
    print_log("\nSUMMARY INFO: for user- ", u)
    data_user = data.query('user', u)
    summarizeData(data_user)

#---------------------------------------------#
