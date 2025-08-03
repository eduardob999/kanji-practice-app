import csv
import os
import re

input_file = 'practicejapanese/data/N5Vocab.csv'
temp_file = 'practicejapanese/data/N5Vocab_temp.csv'

# Kanji unicode range: \u4E00-\u9FFF
kanji_pattern = re.compile(r'[\u4E00-\u9FFF]')

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(temp_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    for row in reader:
        # Check if first column contains kanji
        if row and kanji_pattern.search(row[0]):
            writer.writerow(row)

os.replace(temp_file, input_file)
