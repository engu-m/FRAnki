"""creates ankideck from dictionary of words"""

from unidecode import unidecode
import genanki


class AnkiNote(genanki.Note):
    """extend genanki Note to handle unique guis and not random
    (allows to overwrite cards in deck)"""

    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


def create_card_model(card_fields, model_id):
    css = open("resources/anki_cards.css", "r", encoding="utf-8").read()
    question_html_template = open(
        "resources/card_question.html", "r", encoding="utf-8"
    ).read()
    answer_html_template = open(
        "resources/card_answer.html", "r", encoding="utf-8"
    ).read()

    card_model = genanki.Model(
        model_id,
        "Vocabulaire FR",
        fields=[{"name": field} for field in card_fields],
        templates=[
            {
                "name": "Trouver la définition",
                "qfmt": question_html_template,
                "afmt": answer_html_template,
            },
        ],
        css=css,
    )
    return card_model


def create_empty_deck(deck_name, deck_id):
    return genanki.Deck(deck_id, deck_name)


def fill_deck(new_deck, card_model, dictionary, card_model_fields):
    media_files = []
    for dico_entry in dictionary:
        note_fields = [dico_entry.get(field, "") for field in card_model_fields]
        media_files.append(unidecode(dico_entry.get("img_save_path", "")))
        note = AnkiNote(
            model=card_model,
            fields=note_fields,
        )
        new_deck.add_note(note)
    return new_deck, media_files


def save_deck(deck, media_files, deck_path):
    genanki.Package(deck, media_files).write_to_file(deck_path)


def create_and_save_deck_from_scratch(
    card_fields,
    word_dictionary,
    model_id=8455775866,
    deck_id=7401263646,
    deck_name="Vocabulaire FR",
    deck_path="Voc_FR.apkg",
):
    card_model = create_card_model(
        card_fields,
        model_id=model_id,
    )
    new_deck = create_empty_deck(deck_name=deck_name, deck_id=deck_id)
    updated_deck, media_files = fill_deck(
        new_deck, card_model, word_dictionary, card_model_fields=card_fields
    )
    save_deck(updated_deck, media_files, deck_path)
