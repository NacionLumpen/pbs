"""
Module to parse comments from source code.
"""
import re
import os.path


class Parser(object):
    """
    A Parser is in charge of splitting documentation comments from source code.
    """

    LANGUAGE = {
        ".c": "C"
    }

    def __init__(self):
        self.comment_start = " * "
        self.reviewed_comment = self.comment_start + "@pbs: reviewed"
        self.procedure_pattern = re.compile(r"\w+ \w+\(.*\)")

    def parse(self, source_code_lines):
        """
        Parses a list of source code lines into a dictionary keyed by
        procedure, holding comment lines as lists.
        """
        parsed = {}
        comments_buffer = []
        skip_procedure = False
        for line in source_code_lines:
            if line == self.reviewed_comment:
                skip_procedure = True
            if line.startswith(self.comment_start):
                comments_buffer.append(line.strip(self.comment_start).strip())
            elif self.procedure_pattern.match(line) and not skip_procedure:
                parsed[line] = " ".join(comments_buffer)
                comments_buffer = []
                skip_procedure = False
        return parsed

    def infer_language(self, filename):
        """
        Infers the implementation language from a filename
        """
        _, extension = os.path.splitext(filename)
        return self.LANGUAGE[extension]
