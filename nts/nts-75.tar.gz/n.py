#! /usr/bin/env python

import sys
def main():
    if len(sys.argv) >= 2 and sys.argv[1] == 'w':
        try:
            import nts.ntsWX
            nts.ntsWX.main()
        except:
            print('Errors importing nts.ntsWX ')
            print(sys.exc_info())
    else:
        import nts.ntsData
        nts.ntsData.main()

if __name__ == "__main__":
    main()