import argparse
import os

import yaml


APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def main():
    # create parser and get parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='host of database', type=str)
    parser.add_argument('port', help='port of database', type=int)
    parser.add_argument('user', help='user of database', type=str)
    parser.add_argument('password', help='user password', type=str)
    args = parser.parse_args()

    # load settings of database to file
    db_config_filename = os.path.join(APP_DIR, 'app_config.yaml')
    with open(db_config_filename, 'w') as file:
        yaml.dump(vars(args), file)


if __name__ == "__main__":
    main()
