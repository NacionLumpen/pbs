"""
Main module
"""
import os
import logging

import pbs.build
import pbs.comments
import pbs.lookup

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)


def main():
    """Main entry point."""
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    parser = pbs.comments.Parser()
    for filename in os.listdir(current_dir):
        language = parser.infer_language(filename)
        with open(filename, 'r') as source_file:
            procedure_comments = parser.parse(source_file.readlines())
        for procedure, comments in procedure_comments.iteritems():
            answer = pbs.lookup.search(comments + " in " + language)
            logging.info(
                "Found this answer for procedure '%s' described as '%s':\n %s",
                procedure, comments, answer)
        pbs.build.ccompile(filename)
    pbs.build.clink_many(current_dir, project_name)


if __name__ == '__main__':
    main()
