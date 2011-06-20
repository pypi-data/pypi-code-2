import Tkinter, multiprocessing, os

def main():
    root = Tkinter.Tk()
    lb = Tkinter.Label(root)
    lb.pack()
    try:
        print 'starting'
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        root.quit()

if __name__ == '__main__':
    #proc = multiprocessing.Process(None, main)
    #proc.start()
    pid = os.fork()
    if not pid:
        main()
    else:
        print 'Child', pid
