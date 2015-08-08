import os
import logging

import pbs.build
import pbs.lookup

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)


def main():
    """Main entry point."""
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    for filename in os.listdir(current_dir):
        with open(filename, 'r') as source_file:
            doc, _ = pbs.build.parse(source_file.readlines())
        for comment in doc:
            answer = pbs.lookup.search(comment)
            logging.info("Found this answer:\n %s", answer)
        pbs.build.ccompile(filename)
    pbs.build.clink_many(current_dir, project_name)


if __name__ == '__main__':
    main()
