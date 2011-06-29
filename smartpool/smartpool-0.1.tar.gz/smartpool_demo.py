import time
from smartpool.pool import Pool

def fun(a):
    time.sleep(3)
    return a+1

if __name__ == '__main__':
    p = Pool(processes=8)
    res = p.apply_async(fun, args=[3])
    for trace in p.get_tracebacks():
        print trace
        print '-' * 50
    res.get()
    
    print '=' * 80
    results = []
    p.resize(2)
    time.sleep(2)
    for i in range(0, 7):
        results.append(p.apply_async(fun, args=[i]))
    for r in results:
        print r.get()

    