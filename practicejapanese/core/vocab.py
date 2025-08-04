import csv

def load_vocab(path):
    vocab_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            if row[0].strip():
                # word, reading, meaning, vocab_score, filling_score
                vocab_list.append((row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip()))
    return vocab_list