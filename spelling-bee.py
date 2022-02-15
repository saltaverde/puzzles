import json
import argparse
import multiprocessing


MINIMUM_WORD_LENGTH = 4
DISTINCT_LETTER_COUNT = 7
DICTIONARY_FILE_PATH = '/usr/share/dict/american-english'


def partition(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def assign_to_map(data):
    base_word_map, candidates = data
    sub_map = {}

    for candidate in candidates:
        key = set(candidate)
        for k in base_word_map:
            if key.issubset(k):
                sub_map.setdefault(k, set()).add(candidate)

    return sub_map


def populate_word_map():
    word_map = {}

    with open(DICTIONARY_FILE_PATH) as f:
        candidates = {
            word for word in f.read().split()
            # filter out proper nouns
            if word[0].islower()
            and len(word) >= MINIMUM_WORD_LENGTH
            # no possessives
            and not word.endswith("'s")
        }

    for candidate in candidates:
        # sort the distinct letters in each word
        key = ''.join(sorted({ l for l in candidate }))
        if len(key) == DISTINCT_LETTER_COUNT:
            word_map.setdefault(key, set()).add(candidate)

    with multiprocessing.Pool() as pool:
        results = pool.map(assign_to_map,
            (
                (word_map, cands) for cands in partition(list(candidates), int(len(candidates)/multiprocessing.cpu_count()) + 1)
            )
        )

    for result in results:
        for key, values in result.items():
            word_map[key] |= values

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
