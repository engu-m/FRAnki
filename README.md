# FRAnki 🇫🇷📝

Learn the meaning of unknown **FR**ench words you have encountered with **Anki**!

Read the full blog post explaining what this repo is about [here](https://engu-m.github.io).

## Installation

Clone the repository and install the requirements, with `pip install -r requirements.txt` (`python >= 3.9`). It may also require Firefox.

## Usage

To start with your own (french) words, edit the file `mots nouveaux.txt` with your own words then run `main.py`. This should update `Voc_FR.apkg` which you can import to Anki Desktop.

## Handling failure cases

If the word you are asking for does not exist on the CNRTL (such as the german word Streichholzschächtelchen), it will be added to the list of unknown words under `data/mots non trouvés.txt` so that you can manually look for it and add it to anki.

The web scraper cannot retrieve multiple meanings ; only the first one is saved.
