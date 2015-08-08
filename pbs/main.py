import os
import logging

import pbs
import lookup


def main():
    """Main entry point."""
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    for filename in os.listdir(current_dir):
        with open(filename, 'r') as source_file:
            doc, _ = pbs.parse(source_file.read())
        for comment in doc:
            answer = lookup.search(comment)
            logging.info("Found this answer: %s", answer)
        pbs.ccompile(filename)
    pbs.clink_many(current_dir, project_name)


if __name__ == '__main__':
    main()
