import glob, time

from . import stat
from .util import div, pct

class CPU(object):
    def __init__(self, cpuid):
        self.id = cpuid

        # TODO: /proc/cpuinfo

    def utilization(self, sample_time=0.1):
        utils1 = [int(v) for v in stat.read()['cpu%s' % self.id][:4]]
        time.sleep(sample_time)
        utils2 = [int(v) for v in stat.read()['cpu%s' % self.id][:4]]
        
        used = sum([b - a for (a, b) in zip(utils1[:3], utils2[:3])])
        total = sum([b - a for (a, b) in zip(utils1, utils2)])
        return pct(div(float(used), total))

class CPUs(object):
    @staticmethod
    def count():
        return len(glob.glob('/proc/acpi/processor/CPU*'))

    def __init__(self):
        self.cpus = [CPU(cpuid) for cpuid in range(CPUs.count())]
        
    def __iter__(self):
        return iter(self.cpus)

    def display(self):
        return 'CPU: ' + ' '.join(['{0:3}%'.format(c.utilization()) for c in self])
    
    @staticmethod
    def name():
        return 'linseed_cpus'

    @staticmethod
    def description(short=True):
        return 'CPU utilization information'
    
def main():
    print('--- CPU info ---')
    print(str(CPUs()))

if __name__ == '__main__':
    main()
