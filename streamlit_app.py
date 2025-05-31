import streamlit as st
import nltk
import re
from nltk.corpus import cmudict

nltk.download('cmudict')
pronouncing_dict = cmudict.dict()

phoneme_maps = {
    'English': { 'AA': 'ah', 'AE': 'a', 'AH': 'uh', 'AO': 'aw', 'AW': 'ow', 'AY': 'eye',
        'B': 'b', 'CH': 'ch', 'D': 'd', 'DH': 'th', 'EH': 'e', 'ER': 'er', 'EY': 'ay', 'F': 'f',
        'G': 'g', 'HH': 'h', 'IH': 'i', 'IY': 'ee', 'JH': 'j', 'K': 'k', 'L': 'l', 'M': 'm',
        'N': 'n', 'NG': 'ng', 'OW': 'oh', 'OY': 'oy', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'sh',
        'T': 't', 'TH': 'th', 'UH': 'oo', 'UW': 'oo', 'V': 'v', 'W': 'w', 'Y': 'y', 'Z': 'z', 'ZH': 'zh'
    },
    'Hindi': {
        'a': 'uh', 'e': 'ay', 'i': 'ee', 'o': 'oh', 'u': 'oo', 'm': 'm', 'l': 'l', 'n': 'n',
        'r': 'r', 's': 's', 't': 't', 'k': 'k', 'd': 'd', 'b': 'b', 'g': 'g', 'h': 'h', 'y': 'y',
        'z': 'z', 'p': 'p', 'v': 'v', 'j': 'j', 'f': 'ph', 'w': 'v', 'c': 'ch', 'x': 'ks', 'q': 'k'
    },
    'Spanish': {
        'a': 'ah', 'e': 'eh', 'i': 'ee', 'o': 'oh', 'u': 'oo', 'm': 'm', 'l': 'l', 'n': 'n',
        'r': 'rr', 's': 's', 't': 't', 'k': 'k', 'd': 'd', 'b': 'b', 'g': 'g', 'h': '', 'y': 'y',
        'z': 's', 'p': 'p', 'v': 'b', 'j': 'h', 'f': 'f', 'w': 'gu', 'c': 'k', 'x': 'ks', 'q': 'k'
    },
    'French': {
        'a': 'ah', 'e': 'uh', 'i': 'ee', 'o': 'oh', 'u': 'oo', 'm': 'm', 'l': 'l', 'n': 'n',
        'r': 'r', 's': 's', 't': 't', 'k': 'k', 'd': 'd', 'b': 'b', 'g': 'g', 'h': '', 'y': 'ee',
        'z': 'z', 'p': 'p', 'v': 'v', 'j': 'zh', 'f': 'f', 'w': 'v', 'c': 'k', 'x': 'ks', 'q': 'k'
    },
    'Japanese': {
        'a': 'ah', 'e': 'eh', 'i': 'ee', 'o': 'oh', 'u': 'oo', 'm': 'm', 'l': 'r', 'n': 'n',
        'r': 'r', 's': 's', 't': 't', 'k': 'k', 'd': 'd', 'b': 'b', 'g': 'g', 'h': 'h', 'y': 'y',
        'z': 'z', 'p': 'p', 'v': 'b', 'j': 'j', 'f': 'f', 'w': 'w', 'c': 'k', 'x': 'ks', 'q': 'k'
    }
}

def get_phonemes(word, lang='English'):
    word = word.lower()
    if lang == 'English' and word in pronouncing_dict:
        return pronouncing_dict[word][0]
    else:
        return basic_fallback(word, lang)

def simplify_phonemes(phonemes, lang='English'):
    if lang == 'English':
        simplified = []
        for phoneme in phonemes:
            base = ''.join([c for c in phoneme if not c.isdigit()])
            simplified.append(phoneme_maps[lang].get(base, base))
        return ' - '.join(simplified)
    else:
        return ' - '.join(phonemes)

def basic_fallback(name, lang='English'):
    name = name.lower()
    syllables = re.findall(r'[bcdfghjklmnpqrstvwxyz]*[aeiou]+[bcdfghjklmnpqrstvwxyz]*', name)
    fmap = phoneme_maps.get(lang, phoneme_maps['English'])
    result = []
    for syl in syllables:
        result.append(''.join(fmap.get(c, c) for c in syl))
    return result if result else ['(fallback failed)']

# Streamlit UI
st.title("Name to Phonetic Spelling")
st.write("Enter a name to get a language-style phonetic breakdown")

# Language selector (default = English)
language = st.selectbox("Select language style", list(phoneme_maps.keys()), index=0)

name_input = st.text_input("Enter a name:")

if name_input:
    phonemes = get_phonemes(name_input, language)
    simplified = simplify_phonemes(phonemes, language)
    st.markdown("### Phonetic Spelling")
    st.write(simplified)