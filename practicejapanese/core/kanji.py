import csv

def load_kanji(path):
    kanji_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("Kanji"):
                continue
            level = (row.get("Level") or "").strip()
            kanji_list.append((
                row["Kanji"].strip(),
                row["Readings"].strip(),
                row["Meaning"].strip(),
                row["Score"].strip(),
                level
            ))
    return kanji_list