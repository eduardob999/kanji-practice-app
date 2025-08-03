import csv
import random

CSV_PATH = "data/N5Kanji.csv"

def load_kanji_data(path):
    kanji_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            kanji = row[0]
            readings = row[1]
            meaning = row[2]
            kanji_list.append((kanji, readings, meaning))
    return kanji_list

def quiz(kanji_list):
    item = random.choice(kanji_list)
    print(f"Readings: {item[1]}")
    print(f"Meaning: {item[2]}")
    answer = input("What is the Kanji? ")
    if answer == item[0]:
        print("Correct!")
    else:
        print(f"Incorrect. The correct Kanji is: {item[0]}")

if __name__ == "__main__":
    kanji_list = load_kanji_data(CSV_PATH)
    try:
        while True:
            quiz(kanji_list)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")