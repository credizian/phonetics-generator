import streamlit as st
import nltk
import re
from nltk.corpus import cmudict

# Ensure CMU dictionary is available
nltk.download('cmudict')
pronouncing_dict = cmudict.dict()

# “Human‐friendly” phoneme → rough text
phoneme_maps = {
    'English': {
        'AA': 'ah', 'AE': 'a',   'AH': 'uh',  'AO': 'aw',  'AW': 'ow',  'AY': 'eye',
        'B':  'b',  'CH': 'ch',  'D':  'd',   'DH': 'th',  'EH': 'eh',  'ER': 'er',
        'EY': 'ay', 'F':  'f',   'G':  'g',   'HH': 'h',   'IH': 'ih',  'IY': 'ee',
        'JH': 'j',  'K':  'k',   'L':  'l',   'M':  'm',   'N':  'n',   'NG': 'ng',
        'OW': 'oh', 'OY': 'oy',  'P':  'p',   'R':  'r',   'S':  's',   'SH': 'sh',
        'T':  't',  'TH': 'th',  'UH': 'oo',  'UW': 'oo',  'V':  'v',   'W':  'w',
        'Y':  'y',  'Z':  'z',   'ZH': 'zh'
    },
    'Hindi': {
        'a':'uh','e':'ay','i':'ee','o':'oh','u':'oo','m':'m','l':'l','n':'n',
        'r':'r','s':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'h','y':'y',
        'z':'z','p':'p','v':'v','j':'j','f':'ph','w':'v','c':'ch','x':'ks','q':'k'
    },
    'Spanish': {
        'a':'ah','e':'eh','i':'ee','o':'oh','u':'oo','m':'m','l':'l','n':'n','r':'rr',
        's':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'','y':'y','z':'s','p':'p',
        'v':'b','j':'h','f':'f','w':'gu','c':'k','x':'ks','q':'k'
    },
    'French': {
        'a':'ah','e':'uh','i':'ee','o':'oh','u':'oo','m':'m','l':'l','n':'n','r':'r',
        's':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'','y':'ee','z':'z','p':'p',
        'v':'v','j':'zh','f':'f','w':'v','c':'k','x':'ks','q':'k'
    },
    'Japanese': {
        'a':'ah','e':'eh','i':'ee','o':'oh','u':'oo','m':'m','l':'r','n':'n','r':'r',
        's':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'h','y':'y','z':'z','p':'p',
        'v':'b','j':'j','f':'f','w':'w','c':'k','x':'ks','q':'k'
    }
}

# ARPAbet vowel phonemes for English‐syllable grouping
vowel_set = {
    'AA','AE','AH','AO','AW','AY','EH','ER','EY','IH','IY','OW','OY','UH','UW'
}

def format_english(name: str) -> str:
    """
    For English names: look up CMU phonemes, group into syllables by vowel,
    uppercase any syllable containing a primary stress, then join with hyphens.
    """
    word = name.lower()
    if word not in pronouncing_dict:
        return fallback_syllables(word, 'English')

    phonemes = pronouncing_dict[word][0]
    # Build list of syllable‐phoneme lists: each syllable is [(chunk, stress_flag), ...]
    syllable_phonemes = []
    current_syll = []
    for p in phonemes:
        stress = False
        if p[-1].isdigit():
            stress = (p[-1] == '1')
            base = p[:-1]
        else:
            base = p

        chunk = phoneme_maps['English'].get(base, base)
        if base in vowel_set:
            # if current_syll has data, store it before starting new
            if current_syll:
                syllable_phonemes.append(current_syll)
            current_syll = [(chunk, stress)]
        else:
            # attach consonant to existing syllable or start fresh
            if not current_syll:
                current_syll = [(chunk, stress)]
            else:
                current_syll.append((chunk, stress))

    if current_syll:
        syllable_phonemes.append(current_syll)

    # Convert each syllable into a string; uppercase if any stress_flag=True
    output_sylls = []
    for syll in syllable_phonemes:
        syl_str = "".join(chunk for (chunk, sflag) in syll)
        if any(sflag for (_, sflag) in syll):
            syl_str = syl_str.upper()
        output_sylls.append(syl_str)

    return "-".join(output_sylls)


def fallback_syllables(name: str, lang: str) -> str:
    """
    For any language (including English when CMU lookup fails),
    break into vowel‐consonant chunks, map via phoneme_maps[lang],
    then uppercase one chunk by position:
      • If 3+ chunks: uppercase chunk[1]
      • If 2 chunks: uppercase chunk[0]
      • If 1 chunk: uppercase chunk[0]
    Join with hyphens.
    """
    name = name.lower()
    chunks = re.findall(r"[bcdfghjklmnpqrstvwxyz]*[aeiou]+[bcdfghjklmnpqrstvwxyz]*", name)
    fmap = phoneme_maps.get(lang, phoneme_maps['English'])
    mapped = []

    for chunk in chunks:
        if lang == 'English':
            # keep chunk as‐is (lowercase text) for stress heuristic
            mapped.append(chunk)
        else:
            # map each letter to its “chunk” in that language
            mapped.append("".join(fmap.get(c, c) for c in chunk))

    n = len(mapped)
    if n >= 3:
        mapped[1] = mapped[1].upper()
    elif n == 2:
        mapped[0] = mapped[0].upper()
    elif n == 1:
        mapped[0] = mapped[0].upper()

    return "-".join(mapped) or name


# Streamlit UI
st.title("NameDrop‐Style Phonetic Speller")
st.write("Type a name, choose a language, and see a NameCoach-style output.")

name_input = st.text_input("Enter a name:")

language = st.selectbox(
    "Select a language:",
    list(phoneme_maps.keys()),
    index=0  # default = English
)

if name_input:
    if language == "English":
        result = format_english(name_input)
    else:
        result = fallback_syllables(name_input, language)

    st.markdown("### Phonetic Spelling:")
    st.write(f"**{result}**")