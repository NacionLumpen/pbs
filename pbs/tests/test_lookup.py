"""
Tests for the module that looks up the meaning of docstrings in some Web server
"""
import os
from textwrap import dedent

import mock
import nose.tools as nt
from requests.exceptions import ConnectionError

import pbs.lookup


class TestPage(object):
    """
    Tests for the Page class
    """

    @staticmethod
    @mock.patch('requests.get')
    def test_initialize_a_page(mock_get):
        """How to initialize a Page instance."""
        mock_get.text = read_fixed_data('wikipedia.html')
        page = pbs.lookup.Page('http://en.wikipedia.org')
        nt.assert_is_instance(page, pbs.lookup.Page)

    @staticmethod
    @mock.patch('logging.exception')
    @mock.patch('requests.get')
    def test_wrong_initialization(mock_get, mock_log):
        """
        What happens when a Page cannot be instantiated because of
        connection problems.
        """
        url = "any url"
        mock_get.side_effect = ConnectionError("Wrong!")
        assert_not_raises(ConnectionError, pbs.lookup.Page, url)
        mock_log.assert_called_once_with('Error retrieving URL %s', url)


@mock.patch('pbs.lookup.Page.retrieve')
def test_get_links(mock_retrieve):
    """
    How are search hits split from the single results page
    """
    query = "Finalize object in Scala"
    # these were the answers on August 5 2015
    mock_retrieve.return_value = read_fixed_data('test_lookup.dat')
    search_hits = pbs.lookup.get_search_hits(query)
    links = search_hits.links
    nt.assert_equal(10, len(links))
    expected_regexp = (
        r'/url\?q='                     # matched literally
        r'http://stackoverflow\.com'    # matched literally with escaped dot
        r'/questions/\d+'               # question id
        r'/[a-z\-]+'                    # question title
        r'&sa=U&ved=\w{40}&usg=\S{34}'  # params: two hashes
    )
    for link in links:
        nt.assert_regexp_matches(link, expected_regexp)
    expected_titles = [
        'how-to-write-a-class-destructor-in-scala',
        'when-is-the-finalize-method-called-in-java',
        'is-there-a-destructor-for-java',
        'java-memory-leak-destroy-finalize-object',
        'what-guarantees-does-java-scala-make-about-garbage-collection',
        'what-is-the-best-way-to-clean-up-an-object-in-java',
        'what-is-the-cause-of-this-strange-scala-memory-leak',
        'java-executing-a-method-when-objects-scope-ends',
        'luajava-call-methods-on-lua-object-from-java',
        'how-to-prevent-an-object-from-getting-garbage-collected'
    ]
    for link, title in zip(links, expected_titles):
        nt.assert_true(title in link)


@mock.patch('pbs.lookup.Page.retrieve')
def test_get_answer(mock_retrieve):
    """
    How to parse an answer from a set of search results
    """
    query = "define a dynamically growing array in C"
    # these were the results on August 6 2015
    mock_retrieve.side_effect = [
        read_fixed_data('test_lookup_c.dat'),
        read_fixed_data('test_answer_c.dat')]
    links = pbs.lookup.get_search_hits(query)
    answer = pbs.lookup.get_answer(links)
    expected = dedent("""\
    typedef struct {
      int *array;
      size_t used;
      size_t size;
    } Array;

    void initArray(Array *a, size_t initialSize) {
      a->array = (int *)malloc(initialSize * sizeof(int));
      a->used = 0;
      a->size = initialSize;
    }

    void insertArray(Array *a, int element) {
      if (a->used == a->size) {
        a->size *= 2;
        a->array = (int *)realloc(a->array, a->size * sizeof(int));
      }
      a->array[a->used++] = element;
    }

    void freeArray(Array *a) {
      free(a->array);
      a->array = NULL;
      a->used = a->size = 0;
    }""")
    nt.assert_equal(expected, answer)


@mock.patch('pbs.lookup.Page.retrieve')
def test_get_answer_no_code(mock_retrieve):
    """
    What happens when the answer selected does not contain code
    """
    query = "Finalize object in Scala"
    mock_retrieve.side_effect = [
        read_fixed_data('test_lookup.dat'),
        read_fixed_data('test_answer.dat')]
    links = pbs.lookup.get_search_hits(query)
    answer = pbs.lookup.get_answer(links)
    expected = (
        "You might be interested to check out Josh Suereth's scala-arm "
        "project, which provides both monadic and delimited-continuation "
        "based resource management for just this source of use: "
        "http://github.com/jsuereth/scala-arm If you really think that "
        "you need a destructor (i.e. because you think you need to create "
        "the object and then hand it off and never see it again) I'd "
        "recommend reconsidering your application architecture instead... "
        "there is simply no way to make this work reliably on the JVM.")
    nt.assert_equal(expected, answer)


@mock.patch('pbs.lookup.get_search_hits')
@mock.patch('pbs.lookup.get_answer')
def test_search(mock_answer, mock_search_hits):
    """
    What are the steps of a search

    - Searching hits for the query
    - Retrieving the answer given in those hits
    """
    query = "whatever"
    hits = ["first hit", "second hit"]
    mock_search_hits.return_value = hits
    pbs.lookup.search(query)
    mock_search_hits.assert_called_once_with(query)
    mock_answer.assert_called_once_with(hits)


@mock.patch('pbs.lookup.Page.retrieve')
@mock.patch('pbs.lookup.get_search_hits')
def test_search_no_answer(mock_search_hits, mock_retrieve):
    """
    What happens if there is no answer given to a specific query
    """
    query = "asdffgdfg"
    hits = "not valid url"
    mock_search_hits.first_link.return_value = hits
    mock_retrieve.return_value = (
        "<html><head></head><body>404 Not Found</body></html>")
    answer = pbs.lookup.search(query)
    nt.assert_equal(answer, pbs.lookup.NO_ANSWER_MSG)


def assert_not_raises(exception, func, *args, **kwargs):
    """
    Asserts that a function `func` called with `args` and `kwargs` does not
    raise the type of exception called `exception`.
    """
    nt.assert_raises(AssertionError,
                     nt.assert_raises,
                     exception,
                     func, *args, **kwargs)


def read_fixed_data(filename):
    """Returns the contents of a data file located under the test directory."""
    return open(os.path.join(os.getcwd(), 'pbs', 'tests', filename)).read()
