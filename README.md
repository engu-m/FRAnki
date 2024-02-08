# Mots nouveaux

Keywords: web scraping, HTML, CSS

## Description

While reading french, you may encounter new words (mots nouveaux) which you do not know. It happens also to native speakers with literature and though you can infer the meaning of a word thanks to the context, it slows down the reading and may generate misinterpretation.

The goal of this project is to fetch for every word from a list of words a definition, example and illustration image, then to transform this data in anki flashcards and collect them in a deck for further learning. You can then import the Anki deck to your account and study it on the mobile app!

Because I could not find any apprpriate API for dictionary content, and for the sake of honing my skills, I decided to use web scraping from the CNRTL website and from google images.

Example: ...

## Installation

Clone the repository and install the requirements.

## How does it work?

### Word scraper

For the CNRTL, BeautifulSoup is enough as the website is static. The structure is a little messy, some tags are missing but overall I manage to retrieve the first definition and example of the given word.

### Google image scraper

For the Google Image scraper, it is much more difficult.
I had several options:
1) Use google API -> limited to 100 requests per month. Inconvenient since I may have batches of 300+ words
2) Use `bing-image-downloader` module on PyPi -> very fast and convenient, but... research language is set to american english so it may lead to wrong images (e.g. the word ante, which is nothing in english but an architectural feature in french)
3) Do it by hand -> chosen option

The first issue is the waiting screen. When performing a search whitout being logged in on your Google account and without cookies you get the following screen:

!(image)[image]

You need to click on one of the blue buttons. Beautifulsoup cannot handle this so I will have to go along with the package Selenium. The installation is a little more elaborate, but once setup the scraper is ready to go.
