import csv

def load_vocab(path):
    vocab_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("Kanji"):
                continue
            # Keep original tuple order so existing index usage is unchanged, append Level at end
            level = (row.get("Level") or "").strip()
            vocab_list.append((
                row["Kanji"].strip(),
                row["Reading"].strip(),
                row["Meaning"].strip(),
                row["VocabScore"].strip(),
                row["FillingScore"].strip(),
                level
            ))
    return vocab_list