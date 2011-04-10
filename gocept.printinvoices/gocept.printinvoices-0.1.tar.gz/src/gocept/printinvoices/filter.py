# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import re
page_pattern = re.compile('^%%Page: [0-9]+ [0-9]+$')
subseq_pattern = re.compile('(Seite [0-9]+ von [0-9]+ - Rechnung Nr. [0-9]+)')
beginpagesetup_pattern = re.compile('^%%BeginPageSetup$')
endpagesetup_pattern = re.compile('^%%EndPageSetup$')
pdfstartpage_pattern = re.compile('^pdfStartPage$')

tray_cmd = ('<< /ManualFeed false >> '
            'setpagedevice statusdict begin %s setpapertray end\n')


def insert_tray_directives(lines, tray1, tray2):
    pages = [[]]
    for line in lines:
        if page_pattern.match(line):
            pages.append([])
        pages[-1].append(line)

    for line in pages[0]:
        yield line

    for page in pages[1:]:
        for line in page:
            if subseq_pattern.search(line):
                tray = tray2
                break
        else:
            tray = tray1

        page_iter = iter(page)
        for line in page_iter:
            yield line
            if pdfstartpage_pattern.match(line):
                break
        yield tray_cmd % tray
        for line in page_iter:
            yield line
