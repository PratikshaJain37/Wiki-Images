"""
Wiki Images - Main script
Authors : Pratiksha Jain, Deepali Singh

"""

#---------------------------------------------#

# Libraries Used

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

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

    # List of wiki_pages
    usage_on_wikis = []
        

# Attributes of each wiki_page correspond to the name and link of each of the required pages. 
class wiki_page():
    
    name = False

    link = False

#---------------------------------------------#

# STEP 1 - Extracting data from Wiki and storing in a database

# Defining the URL 
URL = 'https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=Tagooty'

# For parsing the content in the mentioned URL
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

# Initialising empty list for staoring wiki_image elements
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

#---------------------------------------------#

# STEP 2:
#2.1 visiting the page for each image (object)
#2.2 accessing section "File usage on other wikis" (if it exists)
#2.3 appending name and link of 'wiki pages' in usage_in_wikis (excluding "Talk:" and "User:")
#2.4 checking if it is a 'Quality Image' or/and 'Featured Image'

for obj in data:  #visiting page for each image (object)

    URL_images = obj.path

    page_images = requests.get(URL_images)

    soup_images = BeautifulSoup(page_images.content, 'html.parser')

    heading = soup_images.find("div", attrs={"id": 'mw-imagepage-section-globalusage'})  #accessing section "File usage on other wikis" (if it exists)

    obj.usage_on_wikis = []
    
    if heading is not None:     #finding 'wiki page' names and links 
        for link in heading.find_all("a", href=True):
            if 'User:' in link["href"] or 'Talk:' in link["href"]:   #filtering "User:" and "Talk:"
                continue
            else:    
                temp_images = wiki_page()
                temp_images.name = link.text        #saving names of each wiki page correspoding the respective image (object) in class wiki_pages()
                temp_images.link = link["href"]     #saving links of each wiki page correspoding the respective image (object) in class wiki_pages()

                obj.usage_on_wikis.append(temp_images)      #appending the wiki_page() database in the list usage_in_wikis

    if 'This image has been assessed using the Quality image guidelines and is considered a Quality image.' in soup_images.text:  #checking if it is a 'Quality Image'
        obj.is_quality_image = True     
    if 'This is a featured picture on' in soup_images.text:  #checking if it is a 'Featured Image'
        obj.is_featured_image = True

#---------------------------------------------#

# Step 3: Putting it in a .csv file

# 'Path' and 'Time Stamp' can be uncommented as per the requirements
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
    
    if obj.usage_on_wikis == []:
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
df.to_csv(r'Wiki_Images.csv', index=False, header=True)
    
#---------------------------------------------#
