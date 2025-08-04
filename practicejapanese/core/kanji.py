import csv

def load_kanji(path):
    kanji_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue
            # Only take kanji, readings, meaning, score
            kanji_list.append((row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()))
    return kanji_list