"""
Functions to parse source code
"""
import re
import shlex
import subprocess as sp


def parse(source_code_lines):
    """
    Parse source code, splitting its contents into documentation and procedure
    definitions

    :param source_code_lines: a list of strings; each string is a line in the
        original source code
    :returns: two lists of strings; the first one contains the documentation
        comments, the second one the procedure signatures.
    """
    doc = []
    proc = []
    comment_start = " * "
    procedure_pattern = re.compile(r"\w+ \w+\(.*\)")
    for line in source_code_lines:
        if line.startswith(comment_start):
            doc.append(line.strip(comment_start))
        elif procedure_pattern.match(line):
            proc.append(line)
    return doc, proc


def __source_to_object_name(file_path):
    return re.sub(r".c$", r".o", file_path)


def ccompile(source_file_path):
    command = "cc -c {source_code} -o {object_code}".format(
        source_code=source_file_path,
        object_code=__source_to_object_name(source_file_path))
    execute(command)


def clink(object_file_path):
    command = "cc {object_code} -o {program}".format(
        object_code=object_file_path,
        program=re.sub(r".o$", r"", object_file_path))
    execute(command)


def make(file_path):
    ccompile(file_path)
    object_path = __source_to_object_name(file_path)
    clink(object_path)


def execute(command):
    sp.call(shlex.split(command))  # pragma: no cover
