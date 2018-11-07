#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals
import argparse

from open_nmt.onmt.utils.logging import init_logger
from open_nmt.onmt.translate.translator import build_translator

import open_nmt.onmt.inputters
import open_nmt.onmt.translate
import open_nmt.onmt
import open_nmt.onmt.model_builder
import open_nmt.onmt.modules
import open_nmt.onmt.opts


def main(opt):
    translator = build_translator(opt, report_score=True)
    translator.translate(src_path=opt.src,
                         tgt_path=opt.tgt,
                         src_dir=opt.src_dir,
                         batch_size=opt.batch_size,
                         attn_debug=opt.attn_debug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='translate.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    open_nmt.onmt.opts.add_md_help_argument(parser)
    open_nmt.onmt.opts.translate_opts(parser)

    opt = parser.parse_args()
    logger = init_logger(opt.log_file)
    main(opt)
