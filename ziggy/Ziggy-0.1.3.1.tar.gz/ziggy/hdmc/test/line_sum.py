#! /usr/bin/env python

import sys

def read_entries(file):
    for line in file:
        line = line.strip()
        key, value = line.split('==HDMC_CHECKPOINT==')
        value = value.strip()
        if len(value) > 0:
            line_data = value.split("==")[2]
            yield key, int(line_data.split()[0])
        
def main():
    linecounts = read_entries(sys.stdin)
    total = 0
    seen_keys = []
    for key, count in linecounts:
        if key not in seen_keys:
            total += count
            seen_keys.append(key)
        
    print str(total) + " total"
    
if __name__ == "__main__":
    main()
    