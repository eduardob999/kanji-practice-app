import csv

def load_kanji(path):
    kanji_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            kanji = row[0].strip()
            readings = row[1].strip()
            meaning = row[2].strip()
            kanji_list.append((kanji, readings, meaning))
    return kanji_list