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

                obj.usage_on_wikis.append(temp_images)      #appending the wiki_pages() database in the list usage_in_wikis

    if 'This image has been assessed using the Quality image guidelines and is considered a Quality image.' in soup_images.text:  #checking if it is a 'Quality Image'
        obj.is_quality_image = True     
    if 'This is a featured picture on' in soup_images.text:  #checking if it is a 'Featured Image'
        obj.is_featured_image = True


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
