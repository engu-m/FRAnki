"""scrape cnrtl to update list of new words"""

import json
import os
import ssl
import urllib
from datetime import datetime
from pathlib import Path
from time import sleep
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from tqdm import trange
from unidecode import unidecode


class Crawler:
    """Scraper for cnrtl website. Can search for a word or a list of words"""

    matching_key_css = {
        "mot": "div#vtoolbar ul li#vitemselected a",
        "code": "div#vtoolbar ul li#vitemselected a",
        "définition": "span.tlf_cdefinition",
        "synonyme": "span.tlf_csynonime i",
        "exemple": "span.tlf_cexemple",
        "auteur": "span.tlf_cexemple span.tlf_cauteur",
        "titre": "span.tlf_cexemple span.tlf_ctitre",
        "date": "span.tlf_cexemple span.tlf_cdate",
    }

    all_fields = matching_key_css.keys()

    def remove_from_str(string, subexprs):
        for subexpr in subexprs:
            if subexpr in string:
                string = string.replace(subexpr, "")
        return string

    additional_transformation = {
        "mot": lambda mot_et_code: Crawler.remove_from_str(
            mot_et_code, ["subst", "fem", "fém", "masc", "plur"]
        )
        .strip(" .,")
        .strip("123456789"),
        "code": lambda mot_et_code: mot_et_code.split(", ")[-1],
        "exemple": lambda full_ex: full_ex[: full_ex.rfind("(")],
    }

    def __init__(self, headless=True) -> None:
        options = Options()
        options.headless = headless
        options.set_preference("intl.accept_languages", "fr-FR")

        driver = webdriver.Firefox(
            executable_path=os.path.abspath(
                "C:/Users/Enguerrand Monard/Desktop/CentraleSupelec/Césure/Préparation stages/tutos info/Jolis mots/geckodriver-v0.31.0-win64/geckodriver.exe"
            ),
            options=options,
        )

        self.driver = driver

    def search_word(self, word):
        """search for one word on cnrtl website"""
        self.driver.get(f"https://www.cnrtl.fr/definition/{word}")

        # Forme introuvable
        unfound_word = self.driver.find_elements(
            by=By.CSS_SELECTOR, value="div#contentbox b"
        )
        if (
            len(unfound_word) > 0
            and unfound_word[0].text == "Cette forme est introuvable !"
        ):
            return [{"mot": word.upper(), "défintion": ""}]

        # Forme incorrecte mais suggestions
        suggestion_word = self.driver.find_elements(
            by=By.CSS_SELECTOR, value="div#contentbox>h2"
        )
        if len(suggestion_word) > 0 and suggestion_word[0].text == "Terme introuvable":
            suggested_words = self.driver.find_elements(
                by=By.CSS_SELECTOR, value="div#contentbox p a"
            )
            suggested_words = [html_word.text for html_word in suggested_words]
            accumulator = []
            # search for suggestions
            for suggestion in suggested_words:
                aux_contenu = self.search_word(suggestion)
                accumulator += aux_contenu
            return accumulator

        # Word found
        contenu = {}
        for category, css in self.matching_key_css.items():
            liste_elem = self.driver.find_elements(by=By.CSS_SELECTOR, value=css)
            if len(liste_elem) > 0:
                if category in self.additional_transformation:
                    category_content = (self.additional_transformation[category])(
                        liste_elem[0].text
                    )
                else:
                    category_content = liste_elem[0].text
                contenu[category] = category_content.strip(", ")

        return [contenu]

    def search_and_save_words(self, filepath, json_path):
        """search for all words in plain text file and save result"""
        accumulator = []
        with open(json_path, "wt+", encoding="utf8") as output_file:
            try:
                dictionary = json.load(output_file)
                all_words = [entree["mot"] for entree in dictionary]
            except json.decoder.JSONDecodeError:
                dictionary = []
                all_words = []
            # scrape web for definitions
            with open(filepath, "rt", encoding="utf-8") as liste_txt:
                all_lines = liste_txt.readlines()
                for i in trange(len(all_lines)):
                    line = all_lines[i].strip()
                    if (
                        line.upper() not in all_words
                    ):  # FIX bug here. should look only to word field, not all json
                        # look only for new words
                        contenu = self.search_word(line)
                        contenu = [
                            content for content in contenu if content.get("définition")
                        ]
                        accumulator = [*accumulator, *contenu]
            # save result
            dico_result = dictionary + [
                entry for entry in accumulator if entry["mot"] not in all_words
            ]
            output_file.seek(0)  # Start the json on first row
            json.dump(
                dico_result,
                output_file,
                ensure_ascii=False,
                indent=2,
            )

    @staticmethod
    def find_words_not_in_json(words_path, json_path, save_path):
        """Given a list of words in .txt and a json database, shows which
        words were not found in cnrtl"""
        not_in_json = []

        with open(json_path, "rt+", encoding="utf8") as json_file:
            try:
                dictionary = json.load(json_file)
                saved_words = [entree["mot"] for entree in dictionary]
            except json.decoder.JSONDecodeError:
                print("FAIL TO OPEN JSON")

        # for all words
        with open(words_path, "rt", encoding="utf-8") as liste_txt:
            all_lines = liste_txt.readlines()
            for i in trange(len(all_lines)):
                word = all_lines[i].strip()
                word_not_in_json = True
                for transformed_dict_word in saved_words:
                    if transformed_dict_word.startswith(word.upper()):
                        word_not_in_json = False
                if word_not_in_json:
                    not_in_json.append(word)

        with open(save_path, "w+", encoding="utf-8") as saved_file:
            saved_file.write("\n".join(not_in_json))

    def image_search(self, word):
        def proper_filename(string):
            string = unidecode(string)
            string = [s for s in string if s.isalnum() or s in list("-_()/.")]
            return "".join(string)

        url = []
        time_to_wait = 1
        while url == [] and time_to_wait < 2:
            self.driver.get(
                f"https://www.google.com/search?q={word}&tbm=isch&hl=fr&gl=fr"
            )
            sleep(time_to_wait)
            tout_refuser_button = self.driver.find_elements(
                by=By.CSS_SELECTOR,
                value="div.VfPpkd-dgl2Hf-ppHlrf-sM5MNb button.LQeN7 span.VfPpkd-vQzf8d",
            )
            if len(tout_refuser_button) > 0:
                tout_refuser_button[0].click()
            image = self.driver.find_elements(
                by=By.CSS_SELECTOR, value="div[data-ri='0'] a img"
            )[0]
            image.click()
            sleep(time_to_wait)  # let the side menu load
            side_imgs = self.driver.find_elements(
                by=By.CSS_SELECTOR, value="img.iPVvYb"
            )
            urls = [side_img.get_attribute("src") for side_img in side_imgs]
            url = [url_img for url_img in urls if "http" in url_img]
            time_to_wait *= 1.2
        try:
            url = url[0]
            # image_content = requests.get(url).content
            str_right_now = datetime.now().strftime("%Y%m%d%H%M%S")
            image_path_str = proper_filename(
                f"./data/images_{version}/{str_right_now}_{word}.jpg"
            )
            image_path = Path(image_path_str)
            ssl_context = ssl._create_unverified_context()
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            # Set the user-agent header and make the request
            headers = {"User-Agent": user_agent}
            req = urllib.request.Request(url, headers=headers)
            with urlopen(req, context=ssl_context) as u:
                image_content = u.read()
            with open(image_path, "wb") as img_file:
                img_file.write(image_content)
            return image_path
        except Exception as e:
            print(f"{e} : An error occured while fecthing/saving {word} - {url}")
            return Path("this_path_does_not_exist")  # and let's keep it that way !


if __name__ == "__main__":
    # search words from new list
    Crawler().search_and_save_words(
        f"./data/liste_mots_{version}.txt",
        f"./data/dictionnaire_{version}.json",
    )
    # find lost words
    Crawler.find_words_not_in_json(
        f"./data/liste_mots_{version}.txt",
        f"./data/dictionnaire_{version}.json",
        f"./data/liste_mots_absents_{version}.txt",
    )
