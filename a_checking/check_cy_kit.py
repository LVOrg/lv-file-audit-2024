import cy_kit
from cyx.common import config
from cyx.repository import Repository
class A:
    config=config
    repository=Repository
    def test(self):
        print("Test")
class B:
    a:A=cy_kit.singleton(A)
    """
    Test class
    """
class C(B):
    pass

b=cy_kit.singleton(B)
c=cy_kit.singleton(C)
c.a.test()
data =c.a.repository.files.app("lv-docs").context.find_one({})
print(data)