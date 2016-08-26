## import all modules
from os import listdir
import pexif
from os.path import isfile, join
import pandas as pd

filename_csv = 'Properties_for_Utt_PhotosTest.csv'

## read the file and create a dictionary with file and title pairs
df = pd.read_csv(filename_csv, header=None)
name_dict = {}

for i, row in df.iterrows():
    try:
        name_dict[row[0]] = row[1]
    except:
        pass

## get all the files in the current directory.
## please place the python script in the same directory
## as the files
onlyfiles = [f for f in listdir('.') if isfile(join('.', f))]

def addTitle(filename, title):
    """Function to add title to a file"""
    # Add exif in a file
    img = pexif.JpegFile.fromFile(filename)
    img.exif.primary.ImageDescription = title
    img.writeFile(filename)


## iterate through each file and add the title
## as given in the csv file
for file in onlyfiles:
    if file.endswith('.jpg'):
        try:
            title = name_dict[file]
            addTitle(file, title)
        except:
            pass


