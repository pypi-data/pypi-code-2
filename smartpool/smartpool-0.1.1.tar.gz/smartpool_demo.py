import time
from smartpool.pool import Pool

def fun(a):
    time.sleep(3)
    return a+1

if __name__ == '__main__':
    p = Pool(processes=8)
    for i in range(0, 8):
        res = p.apply_async(fun, args=[3])
    print '=' * 30, 'Starting traceback test', '=' * 30
    for trace in p.get_tracebacks():
        print trace
        print '-' * 50
    res.get()
    print '=' * 30, 'Ending traceback test', '=' * 30
        
    print '=' * 30, 'Starting Resize Test', '=' * 30
    results = []
    p.resize(2)
    time.sleep(2)
    for i in range(0, 7):
        results.append(p.apply_async(fun, args=[i]))
    for r in results:
        print r.get()
    print '=' * 30, 'Ending Resize Test', '=' * 30
    
    