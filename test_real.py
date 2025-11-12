import sys
import os
sys.dont_write_bytecode = True

# Import and immediately reload
import src.data.statistics
import importlib
importlib.reload(src.data.statistics)

from src.data.statistics import calculate_statistics
import numpy as np

# Test with real data
test_data = np.array([10, 20, 30, 40, 50])
result = calculate_statistics(test_data)
print("TEST RESULT:", result)
print("If this works, your function is fixed!")
