#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : mjcf-coverage.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 03/23/2022
#
# This file is part of lisdf.
# Distributed under terms of the MIT license.

import argparse

from lisdf.parsing_v2.mjcf import MJCFVisitor

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()


def main():
    visitor = MJCFVisitor()
    visitor.set_verbose()
    node = visitor.load_file(args.file)
    print(node)
    from IPython import embed

    embed()


if __name__ == "__main__":
    main()
