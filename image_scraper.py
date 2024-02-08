import ssl
import urllib
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from unidecode import unidecode

css_selector_button_deny_cookies = (
    "div.VfPpkd-dgl2Hf-ppHlrf-sM5MNb button.LQeN7 span.VfPpkd-vQzf8d"
)
css_selector_button_deny_cookies_alternative = "button.tHlp8d div.QS5gu.sy4vM"
# css_selector_images_search_results = "div[data-ri='0'] a img"
css_selector_images_search_results = "img.Q4LuWd"
css_selector_images_search_results_alternative = "img.YQ4gaf"
css_selector_side_panel_bottom = "div.izYTqe"
css_selector_image_side_panel = "img.sFlh5c.pT0Scc"


class ImageCrawler:
    """Image Scraper for google image."""

    def __init__(self, headless=True) -> None:
        options = Options()
        if headless:
            options.add_argument("-headless")
        options.set_preference(
            "intl.accept_languages", "fr-FR"
        )  # this is crucial to get appropriate images

        driver = webdriver.Firefox(
            # executable_path="geckodriver-v0.31.0-win64/geckodriver.exe",
            options=options,
        )

        self.driver = driver


def proper_filename(filename):
    """Remove special characters from filename"""
    filename = unidecode(filename)
    filename = [s for s in filename if s.isalnum() or s in list("-_()/.")]
    return "".join(filename)


def wait_for_element_load(crawler, css, timeout):
    try:
        WebDriverWait(crawler.driver, timeout).until(
            expected_conditions.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    css,
                )
            )
        )
    except TimeoutException:
        print(f"Element '{css}' did not load after {timeout} seconds")
    DOM_element = crawler.driver.find_elements(
        by=By.CSS_SELECTOR,
        value=css,
    )
    return DOM_element


def retrieve_gg_img_url(image_crawler, word, first_word):
    """Get image url from first google search result given the query 'word'"""
    time_to_wait = 10  # unit of waiting time
    gg_search_img_url = f"https://www.google.com/search?q={word}&tbm=isch&hl=fr&gl=fr"
    image_crawler.driver.get(gg_search_img_url)

    if first_word:
        ## If google cookie approval screen pops up
        button_deny_cookies = wait_for_element_load(
            image_crawler, css_selector_button_deny_cookies, time_to_wait
        )
        if len(button_deny_cookies) == 0:
            button_deny_cookies = wait_for_element_load(
                image_crawler,
                css_selector_button_deny_cookies_alternative,
                time_to_wait,
            )
        button_deny_cookies[0].click()
        print(f"\nCookie button clicked for word '{word}'")

    ## Navigate img search results
    images = wait_for_element_load(
        image_crawler, css_selector_images_search_results, time_to_wait
    )
    if len(images) == 0:

        images = wait_for_element_load(
            image_crawler, css_selector_images_search_results_alternative, time_to_wait
        )

    urls = []
    i = 0  # start with first image
    while len(urls) == 0:
        image_to_click = images[i]

        ## Click on image to display side panel
        image_to_click.click()
        # wait for side panel to be fully loaded
        wait_for_element_load(
            image_crawler, css_selector_side_panel_bottom, time_to_wait
        )

        ## Select image from side panel
        side_imgs = wait_for_element_load(
            image_crawler, css_selector_image_side_panel, time_to_wait
        )
        ## Get side panel images urls
        img_src_urls = [side_img.get_attribute("src") for side_img in side_imgs]
        # avoid cached images
        urls = [url_img for url_img in img_src_urls if "http" in url_img]

        i += 1  # move on to next image
    return urls[0]


def save_img_from_url(img_url, image_save_path):
    """Retrieve img using requests and save it at given path"""

    ssl_context = ssl._create_unverified_context()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    # Set the user-agent header and make the request
    headers = {"User-Agent": user_agent}
    req = urllib.request.Request(img_url, headers=headers)
    with urlopen(req, context=ssl_context) as u:
        image_content = u.read()
    with open(image_save_path, "wb") as img_file:
        img_file.write(image_content)


def image_search(crawler, word, first_word):
    """With given web crawler, retrieve the first appropriate google image search result
    for the given word.
    Additional caution if this is the first search of the scraper as google images has a
    cookie screen in this case."""
    str_right_now = datetime.now().strftime("%Y%m%d%H%M%S")
    Path("data/images").mkdir(exist_ok=True)
    img_save_path = Path(proper_filename(f"data/images/{str_right_now}_{word}.jpg"))
    img_url = retrieve_gg_img_url(crawler, word, first_word)
    try:
        save_img_from_url(img_url, img_save_path)
    except HTTPError:
        print(f"Could not fetch image for word '{word}' due to HTTP error")
        return None
    return img_save_path
