# README - wiki_images.py

## Description
A python script to display information about a user's contributions to Wikimedia Commons. A .csv is generated with all the wikipedia pages where the images are used.

## Requirements
The script is mainly Python3.7 compliant.
The libraries needed are:
1. requests 2.24.0
(https://pypi.org/project/requests/)
2. beautifulsoup4 4.9.3
(https://pypi.org/project/beautifulsoup4/)
3. pandas 1.1.3
(https://pypi.org/project/pandas/)
4. tqdm 4.54.0
(https://pypi.org/project/tqdm/)
5. time 
GNU time 1.7

## Installation
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


## Version Log and Features
v1.0: Initial version - Extracts data using webscraping, checks file usage in other wikis, and gives output as a csv file
v1.1: Integration of command line arguments, and different modes. Addition of Summary info
v1.2.1: Fixed bug in counters of summary info. Improved readbility of csv file. 
v1.2.2: Recognition of Valued images
v1.2.3: Added config file 
v1.3: Added support for multiple users (27/3/2010 Chanchla K & TAG)
v1.3.1: Added function for filtering( query(),modified class:list), added summarizeData() function
v1.3.2: Fixed bug #counters_usage_on_wiki
v1.3.3: Fixed bug #config file - now in python


## Future Features 
1. Check last updated and fetch only new information
2. Check for next page button - scrape data from "next page"
3. Reduce rate at which requests are made (concept of (Δt, t))
4. Implement threading
5. Integrate Wikimedia Cimmons API
6. Related Script: Automate filling of metadata


## Maintainers and Contributors
Pratiksha Jain
Deepali Singh
Dr. Timothy A. Gonsalves
Chanchla K.