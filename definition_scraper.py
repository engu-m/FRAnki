"""scrape cnrtl to update list of new words"""

import requests
from bs4 import BeautifulSoup
from tqdm import trange

from utils import matching_css_by_field, remove_page_number, save_word_list

# some light post-processing to apply to retrieved content
additional_transformation = {
    "mot": lambda mot: "".join([tag.text for tag in mot if tag.name != "sup"]),
    "code": lambda mot_et_code: mot_et_code.contents[-1],
    "exemple": lambda exemple_et_date: remove_page_number(
        "".join([tag.text for tag in exemple_et_date if tag.name != "span"])
    ).strip(),
}


def scrape_word(word):
    """retrieve dictionary entry for one word on cnrtl website"""
    url = f"https://www.cnrtl.fr/definition/{word}"
    req = requests.get(url, timeout=15)
    soup = BeautifulSoup(req.content, "html.parser")

    # Word cannot be found on the website
    unfound_word = soup.css.select_one("div#contentbox b")
    if unfound_word and unfound_word.text == "Cette forme est introuvable !":
        return [{"mot": word, "défintion": ""}]

    # Word not found but CNRTL has suggestions (in case of misspelling for example)
    suggestion_word = soup.css.select_one("div#contentbox>h2")
    if suggestion_word and suggestion_word.text == "Terme introuvable":
        suggested_words = soup.css.select("div#contentbox p a")
        suggested_words = [html_word.text for html_word in suggested_words]
        accumulator = []
        # search for suggestions
        for suggestion in suggested_words:
            aux_contenu = scrape_word(suggestion)
            accumulator += aux_contenu
        return accumulator

    # Word found
    dictionary_entry = {}
    for field, css_selector in matching_css_by_field.items():
        # retrieve all fields
        web_content = soup.css.select_one(css_selector)
        if web_content:
            if field in additional_transformation:
                # apply light preprocessing depending on the field
                category_content = (additional_transformation[field])(web_content)
            else:
                category_content = web_content.text
            category_content = category_content.strip(", ")
            dictionary_entry[field] = category_content
        # print(field, category_content, web_content.contents, sep="\n  ",end="\n\n")
    return [dictionary_entry]


def search_words(unknown_words_path):
    """search definition for all words in plain text file"""
    new_dictionary = []
    unfound_words = []

    unknown_words_file = open(unknown_words_path, "rt", encoding="utf-8")
    unknown_words = unknown_words_file.readlines()
    for i in trange(len(unknown_words)):
        unknown_word = unknown_words[i].strip()
        dico_entry = scrape_word(unknown_word)
        unfound_words += [
            entry["mot"] for entry in dico_entry if not entry.get("définition")
        ]
        # keep only words with succesful definition scraping
        dico_entry = [entry for entry in dico_entry if entry.get("définition")]
        new_dictionary = [*new_dictionary, *dico_entry]

    save_word_list(unfound_words, "data/mots non trouvés.txt")
    return new_dictionary
