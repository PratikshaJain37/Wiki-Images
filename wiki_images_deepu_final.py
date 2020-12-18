"""
Wiki Images - Main script
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

For running the script (inside a virtual environment):
(With reference from https://docs.python.org/3/tutorial/venv.html)

1. Setting up the virtual environment in the folder
$ python3 -m venv images_venv

2. Activating the virtual environment 
In Windows:
$ images_venv/Scripts/activate.batIn Linux/Unix:
$ source ./venv/bin/activate
(If you use the csh or fish shells, the alternate is activate.csh and activate.fish)

3. Installing the required libraries
    $ pip3 install requests beautifulsoup4 pandas getopt sys

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
    usage_on_wikis = []  # List of wiki_pages
        

# Attributes of each wiki_page correspond to the name and link of each of the required pages. 
class wiki_page():
    
    name = False
    link = False

#---------------------------------------------#

# Defining System Variables

HELP_MENU = False  #for help options

OUTPUT_FILE = 'Wiki_Images.csv' # Output of program

QUIET_MODE = False  # If no updates to be given while 

USER = 'Tagooty' # for defining which user

MAX_FILES = 500  # max files by user to search

COUNT_ONLY = False # count number of files only, without links

SUMMARY_INFO = True

#---------------------------------------------#

# STEP 1 - Extracting data from Wiki and storing in a database

def parseData(USER='Tagooty', baseurl='https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=', url=False):
    # Defining the URL 
    if not url:
        URL = baseurl + USER
    else:
        URL = url

    # For parsing the content in the mentioned URL
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup

def extractData(soup, MAX_FILES):
    # Initialising empty list for storing wiki_image elements
    data = []

    # Finding required table in the webpage
    table = soup.find("table", attrs={"class": 'mw-datatable listfiles'})

    # Iterating inside all the row elements inside table
    for row in table.tbody.find_all("tr"):

        # Creating an instance of a wiki_image
        temp = wiki_image()

        # For finding its timestamp - can be commented out if not needed
        column = row.find("td", attrs={"class": "TablePager_col_img_timestamp"})
        temp.timestamp = column.text

        # Finding links ('a' tags) in each row
        for link in row.find_all("a", href=True):
        
            # Finding the link which starts with 'File', because that is its title, and access to its wikimedia page
            if link["href"].startswith("/wiki/File:"):
                

                link["title"] = link["title"].replace("File:", "")
                link["title"] = link["title"].replace(".jpg", "")
                
                temp.name = link["title"]

                temp.path = "https://commons.wikimedia.org" + link["href"]
            
                break    
        
        # Adding the wiki_image instance to the database
        data.append(temp)

 
    return data[:min(MAX_FILES, len(data))]

#---------------------------------------------#

# STEP 2:
#2.1 visiting the page for each image (object)
#2.2 accessing section "File usage on other wikis" (if it exists)
#2.3 appending name and link of 'wiki pages' in usage_in_wikis (excluding "Talk:" and "User:")
#2.4 checking if it is a 'Quality Image' or/and 'Featured Image'

#visiting page for each image (object)
def collectData(obj):
    soup_images = parseData(url=obj.path)

    #accessing section "File usage on other wikis" (if it exists)
    heading = soup_images.find("div", attrs={"id": 'mw-imagepage-section-globalusage'})  

    obj.usage_on_wikis = []
    
    #finding 'wiki page' names and links 
    count_dataFiltered = 0  #counter for filtered data
    if heading is not None:     
        for link in heading.find_all("a", href=True):

            #filtering "USER:" and "Talk:"
            if 'USER:' in link["href"] or 'User:' in link["href"]  or 'Talk:' in link["href"]:   
                continue
            else:    
                temp_images = wiki_page()

                #saving names of each wiki page correspoding the respective image (object) in class wiki_pages()
                temp_images.name = link.text  

                #saving links of each wiki page correspoding the respective image (object) in class wiki_pages()      
                temp_images.link = link["href"]     

                #appending the wiki_page() database in the list usage_in_wikis
                obj.usage_on_wikis.append(temp_images)  
                count_dataFiltered = 1      

    #checking if it is a 'Quality Image'
    if 'This image has been assessed using the Quality image guidelines and is considered a Quality image.' in soup_images.text: 
        obj.is_quality_image = True   

    #checking if it is a 'Featured Image'  
    if 'This is a featured picture on' in soup_images.text:  
        obj.is_featured_image = True

    return obj, count_dataFiltered   

#---------------------------------------------#

# Step 3: Putting it in a .csv file

def outputData(data, OUTPUT_FILE, COUNT_ONLY):
    
    if COUNT_ONLY == True:
        headers = [
            'Name',
            'Number of Wikis Featured In',
        ]

        for obj in data:
            df = pd.DataFrame(columns=headers)
            df = df.append({
                            'Name' : obj.name,
                            'Number of Wikis Featured In' : len(obj.usage_on_wikis)
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
        ]

        # Initialisng an empty dataframe to store elements in data
        df = pd.DataFrame(columns=headers)

        # Storing all the required links and infomation in the dataframe - only if they have been used on other wikis
        for obj in data:

            if (obj.usage_on_wikis) == []:
                continue
            
            else:
                
                # In case there are multiple usage_on_wikis links, to make them appear on separate lines
                for index, page in enumerate(obj.usage_on_wikis):
                    if index == 0:
                        df = df.append({
                            'Name' : obj.name,
                            #'Path' : obj.path,
                            #'Time Stamp' : obj.timestamp,
                            'Quality Image' : obj.is_quality_image,
                            'Featured Image' : obj.is_featured_image,
                            "Featured In - Page" : page.name,
                            'Featured In - Link': page.link
                        }, ignore_index=True) 
                    else:
                        df = df.append({
                            "Featured In - Page" : page.name,
                            "Featured In - Link": page.link
                        }, ignore_index=True)
            
        # Giving output in csv file
        df.to_csv(OUTPUT_FILE, index=False, header=True)
        
\

#---------------------------------------------#


if HELP_MENU == True:
    print("help options")
    sys.exit()

if QUIET_MODE == True:
    soup = parseData(USER=USER)
    data = extractData(soup, MAX_FILES)
    count_dataFiltered = 0
    for obj in data: 
        if collectData(obj)[1] == 1:
            count_dataFiltered+=1
    outputData(data, OUTPUT_FILE, COUNT_ONLY)
    print("Exporting Complete. Find the csv file in your folder.")

else: 
    soup = parseData(USER=USER)
    data = extractData(soup, MAX_FILES)
    print("\nData parsered and extracted.")
    count_dataFiltered = 0
    print("")
    for obj, perc in zip(data, tqdm (range(len(data)), desc="Filering data...")): 
        if collectData(obj)[1] == 1:
            count_dataFiltered+=1
    print("Filering complete.")
    outputData(data, OUTPUT_FILE, COUNT_ONLY)
    print("\nExporting Complete. Find the csv file in your folder.")

print("\nSUMMARY INFO:")
print("*Total files found --", len(data))
print("*Total files used --", str(count_dataFiltered) + ", " + str(count_dataFiltered/len(data)*100)+"%")
#print("\*Total links found --", )



