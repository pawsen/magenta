import uuid
import lorem
import datetime
import random
import os
import glob
import sys
from cprgen import CPRGenerator
from PIL import Image, ImageDraw
from random import choices
html_dir = "html"
pages_dir = "pages"
num_files = int(sys.argv[1]) if 1 < len(sys.argv) else 10

# Remove previous files
fileList = glob.glob(html_dir+"/"+pages_dir+"/*")
for filePath in fileList:
    try:
        os.remove(filePath)
    except:
        print("Error while deleting file : ", filePath)

index_file = open(html_dir+"/index.html", "w")
index_file.write("<html><body>\n")

has_cpr_choices = [True, False]
has_cpr_choices_weights = [0.1, 0.9]

document_type_choices = ['html', 'image']
document_type_choices_weights = [0.8, 0.2]

def random_cpr():
  start_date = datetime.date(1900, 1, 1)
  end_date = datetime.date(2020, 1, 1)

  time_between_dates = end_date - start_date
  days_between_dates = time_between_dates.days
  random_number_of_days = random.randrange(days_between_dates)
  random_date = start_date + datetime.timedelta(days=random_number_of_days)

  cpr = choices(CPRGenerator(random_date.strftime("%d%m%y"), "Male").searchCPRPossibilities())[0]

  return cpr

for i in range(0, num_files):

  doc_type = choices(document_type_choices, document_type_choices_weights)[0]
  filename_prefix = str(uuid.uuid4())

  has_cpr = choices(has_cpr_choices, has_cpr_choices_weights)[0]

  cpr = random_cpr()

  t = lorem.text()
  if (has_cpr):
    t = cpr+" "+t

  if doc_type == 'image':
    img = Image.new('RGB', (500, 500), color = 'white')
    d = ImageDraw.Draw(img)
    d.text((10,10), t, fill=(0,0,0))
    filename = filename_prefix+".png"
    img.save(html_dir+"/"+pages_dir+"/"+filename)
  elif doc_type == 'html':
    filename = filename_prefix+".html"
    html_file = open(html_dir+"/"+pages_dir+"/"+filename, "w")
    html_file.write("<html><body>"+t+"</body></html>")
    html_file.close()


  # print(filename)
  index_file.write("<a href='"+pages_dir+"/"+filename+"'>"+filename+"</a><br>\n")

  # print(t)

  

index_file.write("</body></html>")
index_file.close()


