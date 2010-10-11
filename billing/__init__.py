"""
Add lib directory to python path
"""

import os
import sys
from merchant import Merchant

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, 'lib'))
