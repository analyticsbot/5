## import all modules
from os import listdir
import pexif
import pyexiv2
from os.path import isfile, join
import pandas as pd

filename_csv = 'Properties_for_Utt_PhotosTest.csv'

## read the file and create a dictionary with file and title pairs
df = pd.read_csv(filename_csv, header=None)
name_dict = {}

for i, row in df.iterrows():
    try:
        name_dict[str(row[0]).strip()] = str(row[1]).strip()
    except Exception,e:
        pass
        print str(e), 1

## get all the files in the current directory.
## please place the python script in the same directory
## as the files
onlyfiles = [f for f in listdir('.') if isfile(join('.', f))]

def addTitle(filename, title):
    """Function to add title to a file"""
    # Add exif in a file
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    key = 'Exif.Image.ImageDescription'
    metadata[key] = pyexiv2.ExifTag(key, title)
    metadata.write()

## iterate through each file and add the title
## as given in the csv file
for file in onlyfiles:
    if file.endswith('.jpg'):
        try:
            title = name_dict[file]
            addTitle(file, title)
        except Exception,e :
            pass
            print str(e), 2

print 'Done'
