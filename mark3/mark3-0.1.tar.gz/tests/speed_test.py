from mark3.markdown import markdown
import time, os


def test_main(n=100):
    text = open(os.path.join(os.path.dirname(__file__), 
        'speed_test.text')).read()

    tot = 0
    for i in range(n):
        t = time.time()
        markdown(text)
        tot += time.time()-t

    print ('Ran {1} time in {0:.3f} seconds'.format(tot, n))
    print ('{0:.1f} ms per run'.format((tot/n)*1000))

if __name__ == '__main__':
    test_main()
