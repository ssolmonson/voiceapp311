"""
Retrives updates from boston.gov on the coronavirus impact
"""

from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.intents.custom_errors import ParseError
from urllib import request
from mycity.utilities.parsing_utils import escape_characters
from bs4 import BeautifulSoup

INTENT_CARD_TITLE = "CORONAVIRUS (COVID-19) UPDATES"
NEWS_SOUND = "<audio src=\"soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_03\"/><audio src=\"soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_02\"/><audio src=\"soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_01\"/>"
NO_UPDATE_ERROR = "I'm not able to find an update right now. Please try again later."

WELCOME_MESSAGE = "<speak>Here are the latest updates:"
HOMEPAGE_URL = "https://www.boston.gov"
CORONAVIRUS_DETAIL_URL = "https://www.boston.gov/news/coronavirus-disease-covid-19-boston"


def get_coronovirus_update(mycity_request):
    """
    Get the latest information about the coronavirus from boston.gov

    :param mycity_request: MyCityRequestDataModel with the user request for information
    :return: MyCityResponseDataModel containing information from boston.gov
    """
    mycity_response = MyCityResponseDataModel()
    mycity_response.card_title = INTENT_CARD_TITLE
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.should_end_session = True
    try:
        mycity_response.output_speech = _construct_output_speech(
            _get_homepage_text(), _get_coronavirus_detail_text())
        mycity_response.output_speech_type = 'SSML'
    except ParseError:
        mycity_response.output_speech = NO_UPDATE_ERROR

    return mycity_response


def _construct_output_speech(homepage_text, coronavirus_page_text):
    """
    Constructs output speech for the coronvirus update

    :param homepage_text: String containing text from the homepage update
    :param coronavirus_page_text: String containing text from the coronavirus detail webpage
    :return: String for output speech
    """
    text = WELCOME_MESSAGE + homepage_text + NEWS_SOUND + coronavirus_page_text + str("</speak>")
    return text

def _get_html_parser(url):
    """
    Creates a BeautifulSoup parser

    :param url: URL to read and create the parser for
    :return: BeautifulSoup parser
    """
    url = request.urlopen(url)
    parser = BeautifulSoup(url, "html.parser")
    url.close()
    return parser
    

def _get_homepage_text():
    """
    Gets coronavirus update text from Boston.gov homepage

    :return: String with coronavirus update text
    """
    parser = _get_html_parser(HOMEPAGE_URL)

    try:
        coronavirus_article = parser.find(
            'article', about="/reopening-during-covid-19-boston")
        text_div = coronavirus_article.find(
            'div', class_='field-type-text-long')
        return escape_characters(text_div.get_text())
    except:
        raise ParseError


def _get_coronavirus_detail_text():
    """
    Get text from latest updates on the Boston.gov coronavirus detail page

    :return: String with latest update text
    """
    parser = _get_html_parser(CORONAVIRUS_DETAIL_URL)

    try:
        all_items = parser.findAll('div', {"class":"field field-label-hidden field-name-field-left-column field-type-text-long field-items"})
        found_first_address_tag = False
        detail_text = ""
        for child in all_items[0].children:
            if child.name == "ul":
                detail_text = detail_text + child.get_text()
    except:
        raise ParseError

    return escape_characters(detail_text)


