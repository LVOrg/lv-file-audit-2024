
import typing
import inspect
def __ins_generic_class__(cls):
    try:
        return cls.__orig_bases__[0].__origin__==typing.Generic
    except:
        return None
def __get_type__(*args,**kwargs):
    if len(args) > 0:
        _type = args[0]
    else:
        _type = kwargs[list(kwargs.keys())[0]]
    if not inspect.isclass(_type):
        raise ValueError(f"For Generic Class the first arg must be type which Generic Class was derived\n"
                         f"Đối với Lớp chung, đối số đầu tiên phải là loại mà Lớp chung được dẫn xuất\n"
                         f"Exmaple:\n"
                         f"class Test(typing.Generic[T])\n"
                         f"\tdef __init__(self,cls:T, cnn:str):\n"
                         f"\t\t...")
    return _type
def singleton():
    def wrapper(cls):
        setattr(cls,"__instance__",None)
        setattr(cls, "__instance_of_generic__", {})
        setattr(cls, "__ready_instance__", False)
        setattr(cls, "__ready_instance_of_generic_type__", {})
        old_new = getattr(cls,"__new__")
        setattr(cls, "__new__before_wrapper__", old_new)
        gtype = __ins_generic_class__(cls)
        type_args = typing.get_args(cls)
        old_init = getattr(cls,"__init__")
        def new_init(obj,*args, **kwargs):
            if gtype:
                _type = __get_type__(*args, **kwargs)
                if not cls.__ready_instance_of_generic_type__.get(id(_type)):
                    old_init(obj, *args, **kwargs)
                    cls.__ready_instance_of_generic_type__[id(_type)]=obj
            else:
                if not cls.__ready_instance__:
                    old_init(obj,*args, **kwargs)
                    cls.__ready_instance__ = True
        def new_new(_cls, *args, **kwargs):
            if gtype:
                _type = __get_type__(*args, **kwargs)
                if _cls.__instance_of_generic__.get(id(_type)):
                    return _cls.__instance_of_generic__[id(_type)]
                else:
                    _cls.__instance_of_generic__[id(_type)]=super(cls, _cls).__new__(_cls)
                    return _cls.__instance_of_generic__[id(_type)]
            else:
                if not _cls.__instance__:
                    _cls.__instance__ = super(cls, _cls).__new__(_cls)

                return _cls.__instance__

        setattr(cls,"__new__",new_new)
        setattr(cls, "__init__", new_init)

        return cls
    return wrapper
def main():
    import typing
    T = typing.TypeVar("T")
    @singleton()
    class Test(typing.Generic[T]):
        def __init__(self,cls:T, cnn:str):
            t=typing.get_args(type(self))
            print("OK")

    @singleton()
    class SubClass:
        ...

    @singleton()
    class TestB:
        ...
    x= Test[SubClass](cls=SubClass,cnn="123")
    z = Test[SubClass](cls=SubClass, cnn="567")
    y = Test[TestB](cls=TestB,cnn="123")
    print(x==z)
    print(x == y)
    print(SubClass()==SubClass())
    print(TestB() == SubClass())
if __name__ == "__main__":
    main()