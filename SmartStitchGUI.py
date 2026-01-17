import multiprocessing

from gui.launcher import launch

if __name__ == '__main__':
    # Required for multiprocessing on Windows
    multiprocessing.freeze_support()
    launch()
