from collections import namedtuple, defaultdict
import itertools

Word = namedtuple('Word', ('spelling', 'sounds', 'syllables'))
Sound = namedtuple('Sound', ('phoneme', 'stress', 'family',))
EMPTY_SOUND = Sound(None, None, None)

# Here I'm using the terms from wikipedia.  onset is a list of sounds that start
# the syllable.  nucleus is the single vowel sound at the core of the syllable.
# coda is the list of sounds at the end of the syllable.  the stress is the
# level of lexical stress from the vowel.
Syllable = namedtuple('Syllable', ('onset', 'nucleus', 'coda', 'stress'))
EMPTY_SYLLABLE = Syllable([], EMPTY_SOUND, [], None)


# A dict for converting cmudict's lexical stress markers into a score for how
# stressed a sound is.  Consonants get 0, while vowels range from 1 (least
# stressed) to 3 (most stressed).
STRESSES = defaultdict(lambda: 0)
STRESSES.update({
    '1': 3, # Primary lexical stress.
    '2': 2, # Secondary stress.
    '0': 1, # Unstressed.
})

PHONEMES = {
    "AA": "vowel",
    "AE": "vowel",
    "AH": "vowel",
    "AO": "vowel",
    "AW": "vowel",
    "AY": "vowel",
    "B": "stop",
    "CH": "affricate",
    "D": "stop",
    "DH": "fricative",
    "EH": "vowel",
    "ER": "vowel",
    "EY": "vowel",
    "F": "fricative",
    "G": "stop",
    "HH": "aspirate",
    "IH": "vowel",
    "IY": "vowel",
    "JH": "affricate",
    "K": "stop",
    "L": "liquid",
    "M": "nasal",
    "N": "nasal",
    "NG": "nasal",
    "OW": "vowel",
    "OY": "vowel",
    "P": "stop",
    "R": "liquid",
    "S": "fricative",
    "SH": "fricative",
    "T": "stop",
    "TH": "fricative",
    "UH": "vowel",
    "UW": "vowel",
    "V": "fricative",
    "W": "semivowel",
    "Y": "semivowel",
    "Z": "fricative",
    "ZH": "fricative",
}


def parse_line(line):
    spelling, _, sounds_part = line.partition('  ')
    sounds = [parse_sound(s) for s in sounds_part.split()]
    syllables = sounds_to_syllables(sounds)
    return Word(spelling, sounds, syllables)


def parse_sound(s):
    if s[-1].isdigit():
        # We have a vowel.
        phoneme = s[:-1]
        stress = STRESSES[s[-1]]
    else:
        phoneme = s
        stress = 0
    return Sound(phoneme, stress, PHONEMES[phoneme])


def word_distance(w1, w2):
    """
    Given two Word objects, return a score for how different they sound.  Given
    the same word twice, this function should return 0.  The higher the score,
    the more different the words.
    """

    syl_pairs = itertools.izip_longest(
        w1.syllables,
        w2.syllables,
        fillvalue=EMPTY_SYLLABLE
    )
    score = sum(syllable_distance(s1, s2) for s1, s2 in syl_pairs)

    # finger on the scale here.
    # Penalize differences in the first sound more.
    score += (2 if w1.sounds[0] != w2.sounds[0] else 0)
    # Penalize differences in the last sound a bit more
    score += (1 if w1.sounds[-1] != w2.sounds[-1] else 0)
    # Penalize mismatches in syllable counts more.
    score += (2 if len(w1.syllables) != len(w2.syllables) else 0)
    return score


def sounds_distance(ss1, ss2):
    sound_pairs = itertools.izip_longest(
        ss1,
        ss2,
        fillvalue=EMPTY_SOUND
    )
    return sum(sound_distance(s1, s2) for s1, s2 in sound_pairs)


def sound_distance(s1, s2):
    score = 0
    score += (1 if s1.phoneme != s2.phoneme else 0)
    score += (1 if s1.family != s2.family else 0)
    return score


def syllable_distance(syl1, syl2):
    score = 0
    score += (1 if syl1.nucleus.phoneme != syl2.nucleus.phoneme else 0)
    score += (3 if syl1.stress != syl2.stress else 0)

    score += sounds_distance(syl1.onset, syl2.onset)
    score += sounds_distance(syl1.coda, syl2.coda)
    return score


def sounds_to_syllables(sounds):
    """
    Given a list of sounds, group them into syllables.
    """
    vowels = list(get_vowels_positions(sounds))
    v_count = len(vowels)
    syllables = []
    consumed_pos = 0
    for vnum, (pos, v) in enumerate(vowels):
        onset = sounds[consumed_pos:pos]
        consumed_pos = pos + 1
        if vnum < v_count - 1:
            # There's another vowel up ahead.  Decide how many of the consonants
            # between here and there belong to this syllable as opposed to that
            # one.
            next_v_pos, next_v = vowels[vnum+1]
            consonants = sounds[consumed_pos:next_v_pos]
            split = split_consonants(v, consonants, next_v)
            coda = sounds[consumed_pos:consumed_pos + split]
            consumed_pos = consumed_pos + split
        else:
            coda = sounds[consumed_pos:]

        syllables.append(Syllable(onset, v, coda, v.stress))

    return syllables



def get_vowels_positions(sounds):
    """
    Given a list of sounds, yield just the vowels, and their positions.
    """
    for i, s in enumerate(sounds):
        if s.family=='vowel':
            yield i, s


LONG_VOWELS = set(['EY', 'IH', 'AY', 'OW', 'UW'])# A, E, I, O, U
def split_consonants(v1, consonants, v2):
    """
    Given a vowel sound, a list of consonant (non-vowel) sounds, and another
    vowel sound, return the position in the list of consonants where they should
    be split between the syllables.
    """
    # More or less based on http://www.howmanysyllables.com/divideintosyllables

    num = len(consonants)

    # For a single consonant, decide based on whether preceding vowel is long or
    # short.
    if num == 1:
        return 0 if v1.phoneme in LONG_VOWELS else 1

    # For more consonants, give all but the last to the first syllable.
    return num - 1


def get_matching_words(lines, given_words):
    # this is structured a little oddly so we can compute distances for several
    # target words with just one pass through the big word list.
    lookup = {w.spelling: w for w in given_words}
    words_lists = {w.spelling: [] for w in given_words}
    for line in lines:
        if line.startswith(';'):
            continue
        candidate_word = parse_line(line)
        # compute and store distance from candidate word to all given words
        for spelling, word_scores in words_lists.items():
            given_word = lookup[spelling]
            word_scores.append(
                (candidate_word, word_distance(given_word, candidate_word))
            )
    # sort words by distance
    for w in words_lists:
        words_lists[w] = sorted(words_lists[w], key=lambda x: x[1])

    # return an ordered list of scored words for each word we were given
    return [(w[0].spelling + '\n' for w in words_lists[gw.spelling]) for gw in given_words]


def write_word_file(matchword, wordlist, filetype='.txt'):
    with open(matchword.spelling + filetype, 'w') as f:
        f.writelines(wordlist)


def main():
    benedict = parse_line("BENEDICT  B EH1 N AH0 D IH2 K T")
    cumberbatch = parse_line("CUMBERBATCH  K AH1 M B ER0 B AE2 CH")
    with open('custom_dict.txt') as f:
        matches = get_matching_words(f, [benedict, cumberbatch])

    benedicts, cumberbatches = matches

    write_word_file(benedict, benedicts)
    write_word_file(cumberbatch, cumberbatches)

if __name__ == '__main__':
    main()
