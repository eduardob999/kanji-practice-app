import requests
import csv
import json

def fetch_jlpt_csv(level):
    url = f"https://raw.githubusercontent.com/megagonlabs/jlpt-vocab-list/master/{level}.csv"
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)
    words = [row for row in reader]
    return words

def main():
    jlpt_levels = ["n5", "n4", "n3", "n2", "n1"]
    all_words = {}
    for level in jlpt_levels:
        print(f"Fetching JLPT {level.upper()} vocabulary from CSV...")
        words = fetch_jlpt_csv(level)
        all_words[f"jlpt-{level}"] = words
    with open("jmdict.json", "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)
    print("Vocabulary saved to jmdict.json.")

if __name__ == "__main__":
    main()