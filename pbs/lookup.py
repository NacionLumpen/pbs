"""
Module to look up docstring descriptions in remote sites
"""
import logging
from urllib import quote as url_quote

import requests
from pyquery import PyQuery as pq

SEARCH_URL = 'https://www.google.com/search?q=site:{0}%20{1}'
SITE_URL = 'stackoverflow.com'
NO_ANSWER_MSG = '< no answer given >'


def search(query):
    """
    Searches for the given query on a search engine, then gets the answer
    from the links that point to the search hits
    """
    links = get_links(query)
    return get_answer(links)


def get_links(query):
    """
    Get links pointing to answers to a query, out of the results served by a
    search engine about that query
    """
    result = get_result(SEARCH_URL.format(SITE_URL, url_quote(query)))
    html = pq(result)
    return [a.attrib['href'] for a in html('.l')] or \
        [a.attrib['href'] for a in html('.r')('a')]


def get_answer(links):
    """
    Get the answer text from a number of links. The answer will preferently be
    the code associated with the answer; if no code is present, then the
    answer's natural text will be returned.
    """
    # Hardcoded first answer; may later be expanded to get a range of answers
    link = links[0]
    # Remove the '/url?q=' prefix by hand; needs improvement
    link = link[7:]
    page = get_result(link + '?answertab=votes')
    html = pq(page)
    first_answer = html('.answer').eq(0)
    instructions = first_answer.find('pre') or first_answer.find('code')
    if not instructions:
        text = first_answer.find('.post-text').eq(0).text()
    else:
        text = instructions.eq(0).text()
    if text is None:
        text = NO_ANSWER_MSG
    text = text.strip()
    return text


def get_result(url):
    """Retrieves the contents of a URL as text"""
    try:
        return requests.get(url).text
    except requests.exceptions.ConnectionError:
        logging.exception("Error on URL retrieval")
