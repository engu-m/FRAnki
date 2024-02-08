# Mots nouveaux 🇫🇷

Learn the meaning of unknown french words you have encountered!

## Description

While reading french, you may be faced with new words (mots nouveaux) which you do not know. It happens to native speakers as well and even though one can usually infer the meaning of a word thanks to the context, it slows down the reading and may cause misunderstanding.

The goal of this project is to automatically fetch for every one of these words a definition, example and illustration image, then to transform this data in Anki flashcards and gather them in an Anki deck for further learning. You can then import the deck to your account and study it on the mobile app!

Because I could not find any apprpriate API for dictionary content, and for the sake of honing my skills, I decided to use web scraping from the CNRTL website and from google images.

Here are two examples of what an actual flashcard looks like on the mobile app Anki, starting only from the two words as input data. The front and the back of the cards are shown:

![épinoche](https://github.com/engu-m/Mots-nouveaux/assets/85589599/4d4d9d4f-5bfa-46d5-9d1c-5917dac6b058)

![reptation](https://github.com/engu-m/Mots-nouveaux/assets/85589599/87a996a3-cc77-4b9b-8823-af7dead93239)

## Installation

Clone the repository and install the requirements, with `pip install -r requirements.txt` (`python >= 3.9`). It may also require Firefox.

## Usage

To start with your own (french) words, edit the file `mots nouveaux.txt` with your own words then run `main.py`. This should update `Voc_FR.apkg` which you can import to Anki Desktop.

## How does it work?

### Word scraper

The CNRTL (Centre National de Ressources Textuelles et Lexicales) is a website containing a french dictionary among many resources. This is a go-to website to check definitions of french words as it is fast and efficient. Indeed, the pages are very light and the information is quickly seen thanks to overall layout.
For this website, BeautifulSoup is enough as the website is static. The structure of the pages are a little messy and change a bit from one word to another, but in general, I manage to retrieve the first definition and example of the given input word.

### Google image scraper

For the Google Image scraper, it is much more difficult.
I had several options:
1) Use google API -> limited to 100 requests per month. Inconvenient since I may have batches of 200+ words
2) Use `bing-image-downloader` module on PyPi -> very fast and convenient, but... the research language is set to american english so it may lead to wrong images (e.g. the word ante, which is nothing in english but an architectural feature in french)
3) Scrape google images search results by hand -> chosen option

The first issue is the cookie approval screen. When performing a search whitout being logged in on your Google account and with no cookies, you get the following screen:

![image](https://github.com/engu-m/Mots-nouveaux/assets/85589599/a6c11d49-1f64-4e3a-9830-9923adfc36ae)

I need to click on one of the two buttons programatically. Beautifulsoup cannot handle this so I have to go on with the package Selenium. Once the cookie screen is off, the rest of the scraper goes:

![gg_img_scraper](https://github.com/engu-m/Mots-nouveaux/assets/85589599/7f5a99f6-116b-41d3-890c-4af45a120478)

It is better not to download the thumbnail because it is usually not of very good quality.

### Handling fail cases

If the word you are asking for does not exist on the CNRTL (such as the german word Streichholzschächtelchen), it will be added to the list of unknown words under `data/mots non trouvés.txt` so that you can manually look for it and add it to anki.

The web scraper cannot retrieve multiple meanings ; only the first is saved.
