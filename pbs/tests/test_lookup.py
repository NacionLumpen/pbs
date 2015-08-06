"""
Tests for the module that looks up the meaning of docstrings in some Web server
"""
import os
from textwrap import dedent

import mock
import requests.exceptions
from nose.tools import (assert_equal, assert_raises, assert_regexp_matches,
                        assert_true)

import pbs.lookup


@mock.patch('requests.get')
def test_get_result(mock_get):
    """
    How is a request performed for the search of a query
    """
    mock_response = mock.MagicMock()
    mock_response.text = "I have no idea"
    mock_get.return_value = mock_response
    response = pbs.lookup.get_result("How to do something in C")
    assert_equal(response, "I have no idea")


@mock.patch('requests.get')
def test_get_result_wrong(mock_get):
    """
    What happens in case the request goes wrong
    """
    mock_get.side_effect = requests.exceptions.ConnectionError("Boom")
    assert_not_raises(
        requests.exceptions.ConnectionError, pbs.lookup.get_result, "Whatever")


@mock.patch('pbs.lookup.get_result')
def test_get_links(mock_results):
    """
    How are search hits split from the single results page
    """
    query = "Finalize object in Scala"
    # these were the answer on August 5 2015
    mock_results.return_value = open(os.path.join(
        'pbs', 'tests', 'test_lookup.dat')).read()
    links = pbs.lookup.get_links(query)
    assert_equal(10, len(links))
    expected_regexp = (
        r'/url\?q='  # matched literally
        r'http://stackoverflow\.com'  # matched literally with escaped dot
        r'/questions/\d+'  # question id: an integer with one or more digits
        r'/[a-z\-]+'  # question title: lowercase letters and hyphens
        r'&sa=U&ved=\w{40}&usg=\S{34}'  # params, including two hashes
    )
    for link in links:
        assert_regexp_matches(link, expected_regexp)
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
        assert_true(title in link)


@mock.patch('pbs.lookup.get_result')
def test_get_answer(mock_results):
    """
    How to parse an answer from a set of search results
    """
    query = "define a dynamically growing array in C"
    # these were the results on August 6 2015
    mock_results.side_effect = [
        open(os.path.join(os.getcwd(), 'pbs', 'tests',
                          'test_lookup_c.dat')).read(),
        open(os.path.join(os.getcwd(), 'pbs', 'tests',
                          'test_answer_c.dat')).read()]
    links = pbs.lookup.get_links(query)
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
    assert_equal(expected, answer)


@mock.patch('pbs.lookup.get_result')
def test_get_answer_no_code(mock_results):
    """
    What happens when the answer selected does not contain code
    """
    query = "Finalize object in Scala"
    mock_results.side_effect = [
        open(os.path.join(os.getcwd(), 'pbs', 'tests',
                          'test_lookup.dat')).read(),
        open(os.path.join(os.getcwd(), 'pbs', 'tests',
                          'test_answer.dat')).read()]
    links = pbs.lookup.get_links(query)
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
    assert_equal(expected, answer)


def assert_not_raises(exception, func, *args, **kwargs):
    """
    Asserts that a function `func` called with `args` and `kwargs` does not
    raise the type of exception called `exception`.
    """
    assert_raises(AssertionError,
                  assert_raises,
                  exception,
                  func, *args, **kwargs)
