import csv
import random

CSV_PATH = "data/N5Vocab.csv"

def load_vocab_kanji(path):
    vocab_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            kanji = row[0].strip()
            reading = row[1].strip()
            meaning = row[2].strip()
            # Only include entries with a Kanji word
            if kanji:
                vocab_list.append((kanji, reading, meaning))
    return vocab_list

def quiz(vocab_list):
    item = random.choice(vocab_list)
    # Randomly decide to ask for Kanji or Reading
    if random.choice([True, False]):
        print(f"Reading: {item[1]}")
        print(f"Meaning: {item[2]}")
        answer = input("What is the Kanji? ")
        if answer == item[0]:
            print("Correct!")
        else:
            print(f"Incorrect. The correct Kanji is: {item[0]}")
    else:
        print(f"Kanji: {item[0]}")
        print(f"Meaning: {item[2]}")
        answer = input("What is the Reading? ")
        if answer == item[1]:
            print("Correct!")
        else:
            print(f"Incorrect. The correct Reading is: {item[1]}")

if __name__ == "__main__":
    vocab_list = load_vocab_kanji(CSV_PATH)
    try:
        while True:
            quiz(vocab_list)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")