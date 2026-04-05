import fitz
import sys
import glob

files = glob.glob(r"C:\DAD\UK_Lanzarote_Repatriation\Annual accounts\06_Officers_and_Secretaries\Secretary*")
if files:
    doc = fitz.open(files[0])
    print(chr(10).join([page.get_text() for page in doc]))
else:
    print("File not found")
