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


class Page(object):
    """
    Retrieves the contents of an URL and gives access to them in a jQuery-like
    interface.
    """

    def __init__(self, url):
        self.url = url
        self.parsed_contents = pq(self.retrieve())

    def __call__(self, *args, **kwargs):
        return self.parsed_contents(*args, **kwargs)

    def retrieve(self):
        """Retrieves the contents of a URL as text."""
        try:
            return requests.get(self.url).text
        except requests.exceptions.ConnectionError:
            logging.exception("Error on URL retrieval")

    def get_all_links(self):
        """Gets all links from the parsed contents."""
        return [a.attrib['href'] for a in self.parsed_contents('.l')] or \
            [a.attrib['href'] for a in self.parsed_contents('.r')('a')]


class SearchHit(object):
    """
    A SearchHit holds a Page with search hits. This object is responsible for
    parsing all the URLs from the listed search hits.
    """

    def __init__(self, page):
        self.page = page

    @property
    def links(self):
        """Returns all links on the search hits page."""
        return self.page.get_all_links()

    @property
    def first_link(self):
        """
        Returns the first link on the search hits page, and it removes the
        bad prefix ('/url?q=') usually found in these links.
        """
        all_links = self.page.get_all_links()
        first_link = all_links[0]
        return first_link[7:]


class Answer(object):
    """
    An Answer is parsed from the contents of an :class Html:Html instance. It
    has a plain text representation that is either the code contained or the
    natural text in the html, if no code can be found.
    """

    def __init__(self, page):
        self.page = page
        self.first_answer = self.page('.answer').eq(0)
        self.instructions = self.choose_code_or_text()
        self._text = NO_ANSWER_MSG

    def choose_code_or_text(self):
        """
        Chooses either the code found in the answer, or the natural text
        description.
        """
        return self.first_answer.find('pre') or \
            self.first_answer.find('code') or \
            self.first_answer.find('.post-text')

    @property
    def text(self):
        """The text representation of an Answer."""
        if self.instructions:
            self._text = self.instructions.eq(0).text()
        self._text = self._text.strip()
        return self._text


def search(query):
    """
    Searches for the given query on a search engine, then gets the answer
    from the links that point to the search hits
    """
    links = get_search_hits(query)
    return get_answer(links)


def get_search_hits(query):
    """
    Get links pointing to answers to a query, out of the results served by a
    search engine about that query

    :returns: a list of links, as plain text
    """
    page = Page(SEARCH_URL.format(SITE_URL, url_quote(query)))
    search_hits = SearchHit(page)
    return search_hits


def get_answer(search_hits):
    """
    Get the answer text from a number of search hits. The answer will
    preferently be the code associated with the answer; if no code is present,
    then the answer's natural text will be returned.
    """
    link = search_hits.first_link
    html = Page(link + '?answertab=votes')
    return Answer(html).text
