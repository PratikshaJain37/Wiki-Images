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

class wiki_image():

   
    timestamp = False  
    
    name = False
    
    path = False
    
    is_quality_image = None

    is_featured_image = None

    # List of wiki_page s
    usage_on_wikis = []
        

class wiki_page():
    
    name = False

    link = False


#---------------------------------------------#


# STEP 1 - Extracting data from Wiki and storing in a database

URL = 'https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=Tagooty'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

data = []

table = soup.find("table", attrs={"class": 'mw-datatable listfiles'})

for row in table.tbody.find_all("tr"):

    temp = wiki_image()

    column = row.find("td", attrs={"class": "TablePager_col_img_timestamp"})
    temp.timestamp = column.text

    for link in row.find_all("a", href=True):
       
        
        if link["href"].startswith("/wiki/File:"):
            

            link["title"] = link["title"].replace("File:", "")
            link["title"] = link["title"].replace(".jpg", "")
            
            temp.name = link["title"]

            temp.path = "https://commons.wikimedia.org" + link["href"]

        
            break
        

    data.append(temp)


#---------------------------------------------#

# Step 2

for obj in data:

    URL_images = obj.path

    page_images = requests.get(URL_images)

    soup_images = BeautifulSoup(page_images.content, 'html.parser')

    headings = soup_images.find("div", attrs={"id": 'mw-imagepage-section-globalusage'})

    obj.usage_on_wikis = []
    
    if headings is not None:
        for link in headings.find_all("a", href=True):
            if 'User:' in link["href"] or 'Talk:' in link["href"]:
                continue
            else:    
                temp_images = wiki_page()
                temp_images.name = link.text
                temp_images.link = link["href"]

                obj.usage_on_wikis.append(temp_images)
                





#---------------------------------------------#

# Step 3

# Putting it in csv

headers = [
    'Name', 
    #'Path',
    #'Time Stamp',
    'Featured In - Page',
    'Featured In - Link',
    'Quality Image',
    'Featured Image',
]

df = pd.DataFrame(columns=headers)

for obj in data:
    
    if obj.usage_on_wikis == []:
        continue
    else:
        
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
           

df.to_csv(r'test2.csv', index=False, header=True)
    

#---------------------------------------------#
