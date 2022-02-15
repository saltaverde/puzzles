import json
import argparse


def populate_word_map():
    word_map = {}

    with open('/usr/share/dict/american-english', 'r') as f:
        candidates = {word for word in f.read().split() if word[0].islower() and len(word) > 3}

    for candidate in candidates:
        if candidate.endswith("'s"):
            pass
        else:
            key = ''.join(sorted({ l for l in candidate }))
            if len(key) == 7:
                word_map.setdefault(key, set()).add(candidate)

    for candidate in candidates:
        if candidate.endswith("'s"):
            pass
        else:
            key = set(candidate)
            for k in word_map:
                if key.issubset(k):
                    word_map[k].add(candidate)

    with open('spelling-bee-map.json', 'w') as f:
        json.dump({ k: list(v) for k, v in word_map.items() }, f)

    return word_map


def load_word_map():
    try:
        with open('spelling-bee-map.json') as f:
            word_map = json.load(f)
    except:
        word_map = populate_word_map()

    return word_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('letters')
    parser.add_argument('center_letter')
    args = parser.parse_args()

    word_map = load_word_map()

    key = ''.join(sorted(args.letters))

    print(json.dumps(
        sorted(word for word in word_map.get(key) if args.center_letter in word),
        indent=2,
    ))
