from PyPDF2 import PdfFileReader, PdfFileMerger
import os, glob

FINAL_DEST_FOLDER = 'C:\\Users\\Ravi Shankar\\Documents\\Upwork\\law firm\\initial_dest\\'


pdf_files = [f for f in os.listdir(FINAL_DEST_FOLDER) if f.endswith("PDF")]
merger = PdfFileMerger()

##for filename in pdf_files:
##    print filename
##    merger.append(PdfFileReader(os.path.join(FINAL_DEST_FOLDER, filename), "rb"))
##
##merger.write("merged_full.pdf")

import re
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

os.chdir(FINAL_DEST_FOLDER)
for infile in sorted(glob.glob('*.PDF'), key=numericalSort):
    print "Current File Being Processed is: " + infile
    merger.append(PdfFileReader(os.path.join(FINAL_DEST_FOLDER, infile), "rb"))

merger.write("merged_full.pdf")
