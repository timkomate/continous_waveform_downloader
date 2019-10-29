from setup_logger import logger
import pandas as pd

class Processing(object):
    def __init__(self, row):
        print row["client"], row["network"], row["station"]