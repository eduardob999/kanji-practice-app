import os
import csv
def reset_scores():
    print("Resetting all scores to zero...")
    for csv_path in [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Kanji.csv")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv")),
    ]:
        temp_path = csv_path + '.temp'
        updated_rows = []
        with open(csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if row:
                    row[-1] = '0'
                updated_rows.append(row)
        with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(updated_rows)
        os.replace(temp_path, csv_path)
    print("All scores reset to zero.")
import random

def quiz_loop(quiz_func, data):
    try:
        while True:
            quiz_func(data)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")