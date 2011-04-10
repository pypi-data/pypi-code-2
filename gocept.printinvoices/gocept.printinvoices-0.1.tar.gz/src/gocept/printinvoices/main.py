# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.printinvoices.filter
import subprocess
import sys


def process_ps_implementation(tray1, tray2, input, output):
    output_lines = gocept.printinvoices.filter.insert_tray_directives(
        input, tray1=tray1, tray2=tray2)
    for line in output_lines:
        output.write(line)


def process_ps():
    args = sys.argv[1:]
    if not (2 <= len(args) <= 4):
        raise ValueError(
            'Usage: process-ps <tray 1> <tray 2> '
            '[<input file>] [<output file>]')
    tray1, tray2, input, output = (args + [None, None])[:4]
    if input:
        input = open(input)
    else:
        input = sys.stdin
    if output:
        output = open(output, 'w')
    else:
        output = sys.stdout
    process_ps_implementation(tray1, tray2, input, output)


def process_pdf_implementation(tray1, tray2, pdf_path, queue_name):
    pdftops = subprocess.Popen(
        ['pdftops', pdf_path, '-'], stdout=subprocess.PIPE)
    lpr = subprocess.Popen(['lpr', '-P', queue_name], stdin=subprocess.PIPE)
    process_ps_implementation(tray1, tray2, pdftops.stdout, lpr.stdin)
    lpr.stdin.close()
    lpr.wait()
    pdftops.wait()


def process_pdf():
    args = sys.argv[1:]
    if len(args) != 4:
        raise ValueError(
            'Usage: process-pdf <tray 1> <tray 2> <pdf file> <printer queue>')
    tray1, tray2, pdf_path, queue_name = args
    process_pdf_implementation(tray1, tray2, pdf_path, queue_name)
