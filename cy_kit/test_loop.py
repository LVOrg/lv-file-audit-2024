import datetime
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit




# def cal_all():
#     m=1
#
#     @cy_kit.parallel_loop([1,2,300])
#     def test_run(x):
#         fx = x + 12+m
#
#
#         lst =[]
#         @cy_kit.parallel_loop(range(0,fx))
#         def run2(x):
#             return x+3
#
#         lst+=[run2()]
#         return lst
#
#     ret =test_run()
#     return ret

fx="aaaaa"
@cy_kit.watch_forever()
def running(app_name:str):
    def check():
        return datetime.datetime.now().second % 5==0
    def run():
        print(f"{app_name} {fx}")

    return check,run
for x in ["a","b","c"]:
    th = running(x)
    th.start()




