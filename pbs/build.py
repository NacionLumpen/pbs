"""
Functions to parse source code
"""
import os
import re
import shlex
import subprocess as sp
from itertools import ifilter


def __source_to_object_name(file_path):
    """
    Transforms a filename from the convention of source code names to the
    convention of object code names.
    """
    return re.sub(r".c$", r".o", file_path)


def ccompile(source_file_path):
    """Compiles C source code into object code."""
    command = "cc -c {source_code} -o {object_code}".format(
        source_code=source_file_path,
        object_code=__source_to_object_name(source_file_path))
    execute(command)


def clink(object_file_path):
    """Links object code into a program."""
    command = "cc {object_code} -o {program}".format(
        object_code=object_file_path,
        program=re.sub(r".o$", r"", object_file_path))
    execute(command)


def is_object(filename):
    pattern = re.compile(r"\w+.o$")
    return pattern.match(filename) is not None


def all_objects(directory):
    return (fn for fn in ifilter(is_object, os.listdir(directory)))


def clink_many(directory_path, program_name):
    """
    Links all object code files under a directory into a program with the given
    name.
    """
    command = "cc {object_code_list} -o {program}".format(
        object_code_list=" ".join(sorted(all_objects(directory_path))),
        program=program_name)
    execute(command)


def make(file_path):
    """Compiles and links from source code into a program."""
    ccompile(file_path)
    object_path = __source_to_object_name(file_path)
    clink(object_path)


def execute(command):
    """This function executes the given command on the system shell."""
    sp.call(shlex.split(command))  # pragma: no cover
