"""
Tests for the main library module of pbs
"""
import tempfile
import os
import os.path
import shutil
import re
from textwrap import dedent

from nose.tools import assert_equal
from mock import patch, call

import pbs.build


def test_parse():
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
    doc, proc = pbs.build.parse(source_code.splitlines())
    assert_equal(doc, ["this is a doc comment"])
    assert_equal(proc, ["int main()"])


def test_parse_multiline():
    """
    How a single procedure with more than one line in documentation is parsed
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
    doc, proc = pbs.build.parse(source_code.splitlines())
    assert_equal(doc,
                 ["this is a doc comment that stretches over",
                  "more than one line"])
    assert_equal(proc, ["int main()"])


class TestCompile(object):
    """
    How do you use the compile and link methods of pbs
    """

    def __init__(self):
        self.tmpdirname = None
        self.filepath = None
        self.objectpath = None

    def setup(self):
        """
        Variables used by all tests
        """
        self.tmpdirname = tempfile.mkdtemp()
        filename = "example.c"
        self.filepath = os.path.join(self.tmpdirname, filename)
        self.objectpath = re.sub(r".c$", r".o", self.filepath)
        source_code = dedent("""\
            /**
            * this is a doc comment
            */
            int main()
            {
                return 0;
            }
            """)
        with open(self.filepath, "w") as infile:
            infile.write(source_code)

    def teardown(self):
        """
        Cleanup after tests
        """
        shutil.rmtree(self.tmpdirname)

    @patch('pbs.build.execute')
    def test_compile(self, mock_execute):
        """
        How to compile a single file
        """
        pbs.build.ccompile(self.filepath)
        mock_execute.assert_called_once_with(
            "cc -c " + self.filepath + " -o " + self.objectpath)

    @patch('pbs.build.execute')
    def test_link(self, mock_execute):
        """
        How an object file is linked into an executable program
        """
        pbs.build.ccompile(self.filepath)
        pbs.build.clink(self.objectpath)
        program_name = re.sub(r".o$", "", self.objectpath)
        mock_execute.assert_called_with(
            "cc " + self.objectpath + " -o " + program_name)

    @staticmethod
    def test_clink_many():
        """
        How multiple object files are linked into a single executable program
        """
        tmpdir = tempfile.mkdtemp()
        mainfilename = "main.c"
        libfilename = "helper.c"
        headerfilename = "helper.h"
        mainpath = os.path.join(tmpdir, mainfilename)
        libpath = os.path.join(tmpdir, libfilename)
        headerpath = os.path.join(tmpdir, headerfilename)
        with open(mainpath, 'w') as mainfile:
            mainfile.write(dedent("""\
                #include "helper.h"

                int main(int argc, const char *argv[])
                {
                    if (helper_condition()) {
                        return 0;
                    } else {
                        return 1;
                    }
                }
                """))
        with open(libpath, 'w') as libfile:
            libfile.write(dedent("""\
                #include <stdbool.h>

                bool helper_condition() {
                    return true;
                }
                """))
        with open(headerpath, 'w') as headerfile:
            headerfile.write(dedent("""\
                #include <stdbool.h>

                bool helper_condition();
                """))
        pbs.build.ccompile(mainpath)
        pbs.build.ccompile(libpath)
        program_name = "example"
        with patch('pbs.build.execute') as mock_execute:
            pbs.build.clink_many(tmpdir, program_name)
            mock_execute.assert_called_with(
                "cc helper.o main.o -o " + program_name)

    @patch('pbs.build.execute')
    def test_make(self, mock_execute):
        """
        How a source file is compiled and linked into a program
        """
        program_name = re.sub(r".o$", "", self.objectpath)
        pbs.build.make(self.filepath)
        expected_calls = [
            call("cc -c " + self.filepath + " -o " + self.objectpath),
            call("cc " + self.objectpath + " -o " + program_name)]
        assert_equal(mock_execute.call_args_list, expected_calls)
