import sys
from long_test.test_func import add
print(add.__doc__)
print(add(1,2))
print(sys.modules['long_test.test_func'])