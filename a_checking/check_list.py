# my_list: list[str] = ['a','b','c','d','e','f']
#
# for c in my_list:
#     if c=='c':
#         my_list.remove(c)
#     else:
#         print(c)
from sys import getsizeof

my_range = range(0,1000000)
print(getsizeof(my_range))
my_list = list(my_range)
print(getsizeof(my_list))
