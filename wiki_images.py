"""
Wiki Images - Main script
Authors : Pratiksha Jain, Deepali Singh

"""

#---------------------------------------------#

# Libraries Used

import requests
from bs4 import BeautifulSoup
import pandas as pd

#---------------------------------------------#

# Defining classes for database

class wiki_image():

   
    timestamp = None  
    
    name = None
    
    path = None
    
    # List of wiki_page s
    usage_on_wikis = None

    usage_pages = None


class wiki_page():
    
    def __init__(self, name):
        self.name = name
    
    def is_quality_image(self):
        #self.quality_image = True/False
        pass

    def is_featured_image(self):
        #self.featured.image = True/False
        pass


#---------------------------------------------#


# STEP 1 - Extracting data from Wiki and storing in a database

URL = 'https://commons.wikimedia.org/wiki/Special:ListFiles?limit=500&user=Tagooty'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

#print(page)
#print(soup)

#print(soup.title)
#print(soup.title.text)

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



rows = table.tbody.find("tr")
row = wiki_image()


column = rows.find("td", attrs={"class": "TablePager_col_img_timestamp"})
row.timestamp = column.text

for link in rows.find_all("a", href=True):
    if link["href"].startswith("/wiki/File:"):
        

        link["title"] = link["title"].replace("File:", "")
        link["title"] = link["title"].replace(".jpg", "")
        
        row.name = link["title"]

    if link["href"].startswith("https://upload.wikimedia.org/wikipedia"):
        row.path = (link["href"])

      
        break
print(row.timestamp)
print(row.name)
print(row.path)







        

#---------------------------------------------#
