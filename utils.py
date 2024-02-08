import json
import re

matching_css_by_field = {
    "mot": "div#vtoolbar ul li#vitemselected a span",
    "code": "div#vtoolbar ul li#vitemselected a",
    "domaine": "span.tlf_cdomaine",
    "crochet": "span.tlf_ccrochet",
    "définition": "span.tlf_cdefinition",
    "synonyme": "span.tlf_csynonime i",
    "exemple": "span.tlf_cexemple",
    "auteur": "span.tlf_cexemple span.tlf_cauteur",
    "titre": "span.tlf_cexemple span.tlf_ctitre",
    "date": "span.tlf_cexemple span.tlf_cdate",
}

dictionary_fields = matching_css_by_field.keys()

card_fields = list(dictionary_fields) + ["image"]


def save_json(dictionary, json_path):
    """Save list of python dictionaries as JSON at json_path"""
    output_json = open(json_path, "wt+", encoding="utf8")
    output_json.seek(0)  # Start the json on first row
    json.dump(
        dictionary,
        output_json,
        ensure_ascii=False,
        indent=2,
    )
    output_json.close()


def save_word_list(word_list, path):
    with open(path, "at+", encoding="utf-8") as txt_file:
        txt_file.write("\n".join(word_list) + "\n")


def remove_page_number(example_field):
    """Remove expression such as "(p. 610)" or "(p. VI)" from example sentence"""
    roman_nb_regex = r"(?=.)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"
    return re.sub(
        rf" ?\(? ?,? ?p ?\. ?(\d+|{roman_nb_regex}) ?\)? ?\.?", "", example_field
    )
