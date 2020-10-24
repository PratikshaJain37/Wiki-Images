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

'''
page = wiki_page()
page2 = wiki_page()
page3 = wiki_page()

example = wiki_image()
'''

#print(len(example.usage_on_wikis))
#example.usage_on_wikis.extend((page, page2, page3))
#print(len(example.usage_on_wikis))



#---------------------------------------------#


# STEP 1 - Extracting data from Wiki and storing in a database

URL = 'https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=Tagooty'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

#print(page)
#print(soup)

#print(soup.title)
#print(soup.title.text)

#data = [example]
data = []

table = soup.find("table", attrs={"class": 'mw-datatable listfiles'})

#print(table)
#print(table.thead)
#print(table.tbody)


#print(table.tbody.find("tr"))
#print(table.tbody.find_all("tr"))

#for x in table.tbody.find_all("tr"):
    #print(row.find("td", attrs={"class": 'TablePager_col_img_timestamp'}).text)
    #print(x)



for row in table.tbody.find_all("tr"):

    temp = wiki_image()

    column = row.find("td", attrs={"class": "TablePager_col_img_timestamp"})
    temp.timestamp = column.text

    for link in row.find_all("a", href=True):
        if link["href"].startswith("/wiki/File:"):
            

            link["title"] = link["title"].replace("File:", "")
            link["title"] = link["title"].replace(".jpg", "")
            
            temp.name = link["title"]

        if link["href"].startswith("https://upload.wikimedia.org/wikipedia"):
            temp.path = (link["href"])

        
            break

    data.append(temp)
   
#---------------------------------------------#

# Step 2





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
'''
for obj in data:
    
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
'''
for obj in data:
    df = df.append({
        'Name' : obj.name,
        #'Path' : obj.path,
        #'Time Stamp' : obj.timestamp,
        'Quality Image' : obj.is_quality_image,
        'Featured Image' : obj.is_featured_image,
        "Featured In - Page" : obj.usage_on_wikis,
        "Featured In - Link" : obj.usage_on_wikis,
    }, ignore_index=True) 

df.to_csv(r'test.csv', index=False, header=True)
    

#---------------------------------------------#
