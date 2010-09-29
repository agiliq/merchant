"""
Add lib directory to python path
"""

import os
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, 'lib'))