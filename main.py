import json

from tqdm import tqdm
from unidecode import unidecode

from create_deck import create_and_save_deck_from_scratch
from definition_scraper import search_words
from image_scraper import ImageCrawler, image_search
from utils import card_fields, save_json

if __name__ == "__main__":
    ### Definition scraping
    dictionary_never_scraped = True
    if dictionary_never_scraped:
        word_dictionary = search_words("mots nouveaux.txt")
        save_json(word_dictionary, "data/dictionary.json")
        print("Definitions saved")
    else:
        # Load dictionary if you already scraped the CNRTL definitions but not the images
        word_dictionary = json.load(open("data/dictionary.json", "r", encoding="utf-8"))

    ### Image scraping
    print("Loading image scraper")
    image_crawler = ImageCrawler(
        headless=False
    )  # use the same for all images to avoid reloading browser for every image
    print("Image scraper loaded")
    for i, entry in tqdm(enumerate(word_dictionary), total=len(word_dictionary)):
        img_save_path = image_search(
            crawler=image_crawler, word=entry["mot"], first_word=(i == 0)
        )
        if img_save_path:
            entry["image"] = f"<img src='{unidecode(img_save_path.name)}'>"
            entry["img_save_path"] = unidecode(str(img_save_path)).replace("\\", "/")
    save_json(word_dictionary, "data/dictionary.json")

    create_and_save_deck_from_scratch(card_fields, word_dictionary)
