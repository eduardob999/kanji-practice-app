import csv

def load_vocab(path):
    vocab_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            kanji = row[0].strip()
            reading = row[1].strip()
            meaning = row[2].strip()
            if kanji:
                vocab_list.append((kanji, reading, meaning))
    return vocab_list