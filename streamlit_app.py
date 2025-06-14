import streamlit as st
import nltk
import re
from nltk.corpus import cmudict

# === Setup CMU dictionary for English ===
nltk.download('cmudict', quiet=True)
pronouncing_dict = cmudict.dict()

# === Language options with ISO codes ===
language_options = [
    {'value': 'English',  'label': 'English',            'code': 'en'},
    {'value': 'Spanish',  'label': 'Spanish',            'code': 'es'},
    {'value': 'Chinese',  'label': 'Chinese (Mandarin)', 'code': 'zh'},
    {'value': 'Hindi',    'label': 'Hindi',              'code': 'hi'},
    {'value': 'French',   'label': 'French',             'code': 'fr'},
    {'value': 'Arabic',   'label': 'Arabic',             'code': 'ar'},
    {'value': 'Portuguese','label': 'Portuguese',        'code': 'pt'},
    {'value': 'Russian',  'label': 'Russian',            'code': 'ru'},
    {'value': 'Japanese', 'label': 'Japanese',           'code': 'ja'},
    {'value': 'German',   'label': 'German',             'code': 'de'},
    {'value': 'Korean',   'label': 'Korean',             'code': 'ko'},
    {'value': 'Italian',  'label': 'Italian',            'code': 'it'},
    {'value': 'Dutch',    'label': 'Dutch',              'code': 'nl'},
    {'value': 'Turkish',  'label': 'Turkish',            'code': 'tr'},
    {'value': 'Swahili',  'label': 'Swahili',            'code': 'sw'},
]

# === Phoneme / letter maps for supported languages ===
# For languages where we don't have a detailed letter map,
# we fall back to simple chunk splitting.
phoneme_maps = {
    'English': {
        'AA':'ah','AE':'a','AH':'uh','AO':'aw','AW':'ow','AY':'eye',
        'B':'b','CH':'ch','D':'d','DH':'th','EH':'eh','ER':'er','EY':'ay',
        'F':'f','G':'g','HH':'h','IH':'ih','IY':'ee','JH':'j','K':'k',
        'L':'l','M':'m','N':'n','NG':'ng','OW':'oh','OY':'oy','P':'p',
        'R':'r','S':'s','SH':'sh','T':'t','TH':'th','UH':'oo','UW':'oo',
        'V':'v','W':'w','Y':'y','Z':'z','ZH':'zh'
    },
    'Spanish': {
        'a':'ah','e':'eh','i':'ee','o':'oh','u':'oo','m':'m','l':'l','n':'n',
        'r':'rr','s':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'',
        'y':'y','z':'s','p':'p','v':'b','j':'h','f':'f','w':'gu','c':'k',
        'x':'ks','q':'k'
    },
    'Chinese': {},   # fallback splitting
    'Hindi': {
        'a':'uh','e':'ay','i':'ee','o':'oh','u':'oo','m':'m','l':'l','n':'n',
        'r':'r','s':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'h',
        'y':'y','z':'z','p':'p','v':'v','j':'j','f':'ph','w':'v','c':'ch',
        'x':'ks','q':'k'
    },
    'French': {
        'a':'ah','e':'uh','i':'ee','o':'oh','u':'oo','m':'m','l':'l','n':'n',
        'r':'r','s':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'',
        'y':'ee','z':'z','p':'p','v':'v','j':'zh','f':'f','w':'v','c':'k',
        'x':'ks','q':'k'
    },
    'Arabic': {},    # fallback splitting
    'Portuguese':{}, # fallback splitting
    'Russian':{},    # fallback splitting
    'Japanese':{
        'a':'ah','e':'eh','i':'ee','o':'oh','u':'oo','m':'m','l':'r','n':'n',
        'r':'r','s':'s','t':'t','k':'k','d':'d','b':'b','g':'g','h':'h',
        'y':'y','z':'z','p':'p','v':'b','j':'j','f':'f','w':'w','c':'k',
        'x':'ks','q':'k'
    },
    'German': {
        'a':'ah','ä':'eh','b':'b','c':'k','d':'d','e':'eh','f':'f','g':'g',
        'h':'h','i':'ee','j':'y','k':'k','l':'l','m':'m','n':'n','o':'oh',
        'ö':'er','p':'p','q':'kv','r':'r','s':'z','ß':'ss','t':'t','u':'oo',
        'ü':'ue','v':'f','w':'v','x':'ks','y':'y','z':'ts'
    },
    'Korean':{},     # fallback splitting
    'Italian':{
        'a':'ah','b':'b','c':'k','d':'d','e':'eh','f':'f','g':'g','h':'',
        'i':'ee','l':'l','m':'m','n':'n','o':'oh','p':'p','q':'k','r':'r',
        's':'s','t':'t','u':'oo','v':'v','z':'ts'
    },
    'Dutch':{},      # fallback splitting
    'Turkish':{},    # fallback splitting
    'Swahili':{}     # fallback splitting
}

# Vowel set for English syllabification
vowel_set = {'AA','AE','AH','AO','AW','AY','EH','ER','EY','IH','IY','OW','OY','UH','UW'}

# === English CMU-based formatting ===
def format_english(word: str) -> str:
    w = word.lower()
    if w not in pronouncing_dict:
        return fallback_syllables(w, 'English')
    phonemes = pronouncing_dict[w][0]
    sylls = []
    current = []
    for ph in phonemes:
        stress = False
        if ph[-1].isdigit():
            stress = (ph[-1]=='1')
            ph = ph[:-1]
        chunk = phoneme_maps['English'].get(ph, ph)
        if ph in vowel_set:
            if current: sylls.append(current)
            current=[(chunk,stress)]
        else:
            if not current: current=[(chunk,stress)]
            else: current.append((chunk,stress))
    if current: sylls.append(current)
    out=[]
    for s in sylls:
        txt=''.join(ch for ch,_ in s)
        if any(st for _,st in s): txt=txt.upper()
        out.append(txt)
    return '-'.join(out)

# === Fallback for all languages ===
def fallback_syllables(word: str, lang: str) -> str:
    w=word.lower()
    chunks=re.findall(r"[bcdfghjklmnpqrstvwxyz]*[aeiou]+[bcdfghjklmnpqrstvwxyz]*",w)
    fmap=phoneme_maps.get(lang,{})
    mapped=[]
    for c in chunks:
        if fmap:
            mapped.append(''.join(fmap.get(ch,ch) for ch in c))
        else:
            mapped.append(c)
    # stress heuristic: uppercase one chunk by position
    n=len(mapped)
    if n>=3: mapped[1]=mapped[1].upper()
    elif n==2: mapped[0]=mapped[0].upper()
    elif n==1: mapped[0]=mapped[0].upper()
    return '-'.join(mapped) or word

# === Streamlit UI ===
st.title("Name to Phonetic Spelling")
name_input = st.text_input("Enter a name (can include spaces):")
lang = st.selectbox("Select a language:", [opt['value'] for opt in language_options], index=0)

if name_input:
    words = name_input.strip().split()
    results = []
    for w in words:
        if lang=='English':
            results.append(format_english(w))
        else:
            results.append(fallback_syllables(w,lang))
    st.markdown("### Phonetic Spelling:")
    st.write(" ".join(results))