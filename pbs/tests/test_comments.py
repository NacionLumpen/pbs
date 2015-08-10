"""
Test for the module that parses comments from source code.
"""
import unittest
from textwrap import dedent

from nose.tools import assert_equal

import pbs.comments


class TestParser(unittest.TestCase):
    """
    How to use the comments.Parser
    """

    def setUp(self):
        self.parser = pbs.comments.Parser()

    def test_parse_simple(self):
        """
        How a single procedure with a single doc comment is parsed
        """
        source_code = dedent("""\
            /**
             * this is a doc comment
             */
            int main()
            {
                return 0;
            }
        """)
        result = self.parser.parse(source_code.splitlines())
        assert_equal(result, {"int main()": "this is a doc comment"})

    def test_parse_multiline_comment(self):
        """
        How multiline comments are parsed
        """
        source_code = dedent("""\
            /**
             * this is a doc comment that stretches over
             * more than one line
             */
            int main()
            {
                return 0;
            }
        """)
        result = self.parser.parse(source_code.splitlines())
        assert_equal(result, {
            "int main()": ("this is a doc comment that stretches over "
                           "more than one line")})

    def test_parse_multiple_procedures(self):
        """
        How multiple procedures and their comments are parsed
        """
        source_code = dedent("""\
            #include <stdbool.h>

            /**
             * helper method to decide things
             */
            bool helper()
            {
                return true;
            }

            /**
             * this is a doc comment that stretches over
             * more than one line
             */
            int main()
            {
                return 0;
            }
        """)
        result = self.parser.parse(source_code.splitlines())
        assert_equal(result, {
            "bool helper()": "helper method to decide things",
            "int main()": ("this is a doc comment that stretches over "
                           "more than one line")})

    def test_parse_reviewed_procedure(self):
        """
        How to mark a procedure to be skipped because its answer is already
        reviewed.
        """
        source_code = dedent("""\
            /**
             * this is a doc comment
             *
             * @pbs: reviewed
             */
            int main()
            {
                return 0;
            }
        """)
        result = self.parser.parse(source_code.splitlines())
        assert_equal(result, {})

    def test_parser_infers_language(self):
        """
        How to use the parser to infer the implementation language
        """
        filename = "main.c"
        language = self.parser.infer_language(filename)
        assert_equal("C", language)
