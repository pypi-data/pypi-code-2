"""
Markdown speed test.
Usage: speed_test.py [library] [iterations]

library options:
    1 - mark3 (default)
    2 - python-markdown
    3 - python-markdown2"""

import time, os, sys


def test_main(n=50):
    print ('running {0} iterations'.format(n))
    text = open(os.path.join(os.path.dirname(__file__), 
        'speed_test.text')).read()

    tot = 0
    fastest = 900000
    slowest = 0
    for i in range(n):
        t = time.time()
        markdown(text)
        ti = time.time()-t
        tot += ti
        fastest = min(fastest, ti)
        slowest = max(slowest, ti)

    print ('{0:.3f} seconds'.format(tot))
    print ('-'*79)
    print ('Average: {0:.1f} ms'.format((tot/n)*1000))
    print ('Slowest: {0:.1f} ms'.format(slowest*1000))
    print ('Fastest: {0:.1f} ms'.format(fastest*1000))
    print ('-'*79)

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in '123':
        op = '1'
        print (__doc__)
    else:
        op = sys.argv[1]

    print ('-'*79)
    if op == '1':
        from mark3.markdown import markdown
        print ("using mark3")
    elif op == '2':
        from markdown import markdown
        print ("using python-markdown")
    else:
        from markdown2 import markdown
        print ("using python-markdown2")


    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        test_main(int(sys.argv[2]))
    else:
        test_main()
