#!/usr/bin/env python

import argparse
import os
import re


def main():
    parser = argparse.ArgumentParser(description='Tools for DCGAN.')
    parser.add_argument('--fix_samples_filenames', action='store_true', default=False,
                        help='fix file names for samples')
    args = parser.parse_args()

    if args.fix_samples_filenames:
        for f in os.listdir('samples'):
            matches = re.search(r'train_(\d+)_(\d+).png', f)
            if matches is not None:
                filename = 'train_%04d_%04d.png' % (int(matches.groups()[0]), int(matches.groups()[1]))
                os.rename(os.path.join('samples', f), os.path.join('samples', filename))


if __name__ == '__main__':
    main()
