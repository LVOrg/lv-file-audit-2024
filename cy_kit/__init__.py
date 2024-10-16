"""
This library expose a concept was call cy_instance \n
TThư viện này đưa ra khái niệm cy_instance
cy_instance is an instance of Class which was generated by call on of below method: \n
cy_instance là một thể hiện của Lớp được tạo bằng cách gọi phương thức bên dưới \n
    provider, singleton, inject and scope \n
Actually, cy_instance does not create a instance of Class when call cy_kit.provider, cy_kit.singleton, cy_kit.inject or cy_kit.scope \n
Trên thực tế, cy_instance không instance của Lớp khi gọi cy_kit.provider, cy_kit.singleton, cy_kit.inject hoặc cy_kit.scope \n
The real instance of Class will create when thou access any property or method of Class \n
Phiên bản thực của Class sẽ tạo khi bạn truy cập bất kỳ thuộc tính hoặc phương thức nào của Class \n
Example:
    class MyClass:
      def hello():
        print('hello')

    ins = cy_kit.singleton(MyClass) # till now the instance of Class is not ready \n
                                    # cho đến bây giờ, Instance của Class vẫn chưa sẵn sàng
    ins.hello() # The instance of MyClass was created and call hello method
                # after this code the instance of Class will be held in memory and reuse for the next time
                Thể hiện của MyClass đã được tạo và gọi phương thức hello,
                thể hiện của Lớp sẽ được lưu trong bộ nhớ và sử dụng lại cho lần tiếp theo




The library support real useful the way one Class create an instance.\n
The methods list:\n
-----------------------------------------------------------------------------------------------------------\n
| method                    |   description  \n
|__________________________________________________________________________________________________________ \n
| single                    |   Create single instance of Class \n
|                           |   Examaple: ClassA()==ClassA() // is always True \n
|                           |   That means. If thou called thousand time Initialize of Class just only one \n
|                           |     instance create \n
|__________________________________________________________________________________________________________ \n
| instance                  | Create instance of Class \n
|                           | instance: ClassA() == ClassB() // is always false. \n
|                           | That mean everytime thou call Initialize of Class, \n
|                           |     the new instance will create \n
|_____________________________________________________________________________________________________________ \n

The most importance method in the library is "config_provider"
Thou could make several Class with the same in the both method name and args, but difference Implementation of Method.
Then thou can  one of those Class in runtime.
Example:
    class A:
        def hello():
            print ('Hello my name is "A"')
    class B:
        def hello():
            print ('Hello my name is "B"')
    the first code bellow:
        a = cy_kit.single(A)
        a.hello() // thou will see Hello my name is "A"
    the second code bellow
        cy_kit.config_provider(
            from_class=A,
            implement_class = A

        )
        a = cy_kit.single(A)
        a.hello() // thou will see Hello my name is "B"


The purpose of config_provider is help thou needn't re-modify thou's source code, just define a new class and
implement all methods by another way
-------------------------------------------------------- \n

check_implement : will check if class had the both-same method an argument of each method
------------------------------------------------------------------------------- \n
create_logs: create log dir and log file
---------------------------------------------------------------------- \n
get_runtime_type: If thou use cy_kit.config_provider the runtime Type of instance was changed.
In order to get real Type of instance call the methde
-------------------------------------------------------------
Thư viện hỗ trợ thực sự hữu ích theo cách mà một Lớp tạo một thể hiện.\n


config_provider will change any cy_instance with from_class to cy_instance with implement_class \n
    config_provider sẽ thay đổi bất kỳ cy_instance nào với from_class thành cy_instance với implement_class
    Example:
        class A:
            def hello(): print('hello m name A')

        clas B:
            def hello(): print('hello m name B')
        cy_kit.config_provider(
            from_class=A,
            implement_class = B)
        instance = cy_kit.singleton(A)
        instance.hello() #        will see 'hello m name B'
        get_runtime_type( instance) # return Class B

So, if thou wanna to get real Type of Instance Class call
get_runtime_type( instance)
"""
import os.path
import pathlib
import sys
import time
import typing
from typing import TypeVar

__working_dir__ = pathlib.Path(__file__).parent.__str__()

import cy_kit

sys.path.append(__working_dir__)

import cy_kit_x

container = cy_kit_x.container

T = TypeVar('T')


def single(cls: T) -> T:
    """
    Create singleton if Class \n
    Example: \n
        a = cy_kit.single(A) \n
        b = cy_kit.single(A) \n
        print(a==b) //'true' \n
    :param cls:
    :return:
    """
    return cy_kit_x.resolve_singleton(cls)


def instance(cls: T) -> T:
    return cy_kit_x.resolve_scope(cls)


def config_provider(from_class: typing.Union[type,str], implement_class: typing.Union[type,str]):
    """
    config_provider will change any cy_instance with from_class to cy_instance with implement_class \n
    config_provider sẽ thay đổi bất kỳ cy_instance nào với from_class thành cy_instance với implement_class
    Example:
        class A:
            def hello(): print('hello m name A')

        clas B:
            def hello(): print('hello m name B')
        cy_kit.config_provider(
            from_class=A,
            implement_class = B)
        instance = cy_kit.singleton(A)
        instance.hello()
        will see 'hello m name B'
    So, if thou wanna to get real Type of Instance Class call
        cy_kit.get_runtime_type( instance)
    :param from_class:
    :param implement_class:
    :return:
    """
    cy_kit_x.config_provider(from_class, implement_class)


from typing import Generic


# class Provider(Generic[T]):
#     def __init__(self,__cls__:type):
#         self.__cls__=__cls__
#         self.__ins__ =None
#     @property
#     def instance(self)->T:
#         if self.__ins__  is None:
#             self.__ins__ = cy_kit_x.provider(self.__cls__)
#         return self.__ins__


def provider(cls: T) -> T:
    return cy_kit_x.provider(cls)


def check_implement(from_class: type, implement_class: T) -> T:
    cy_kit_x.check_implement(from_class, implement_class)
    return implement_class


def must_imlement(interface_class: type):
    return cy_kit_x.must_implement(interface_class)


def trip_content(data):
    """
    Remove any white space in left and right of data if data is text
    In the case of data is Dictionary.
    The method will detect all values in data and remove any white space in left and right
    -----------------------------------------------------------\n
    Xóa mọi khoảng trắng ở bên trái và bên phải của dữ liệu nếu dữ liệu là văn bản
    Trong trường hợp dữ liệu là Dictionary.
    Phương pháp này sẽ phát hiện tất cả các giá trị trong dữ liệu và xóa mọi khoảng trắng ở bên trái và bên phải
    :param data:
    :return:
    """
    if hasattr(cy_kit_x, "trip_content") and callable(cy_kit_x.trip_content):
        return cy_kit_x.trip_content(data)
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.rstrip(' ').lstrip(' ')
            elif isinstance(v, dict):
                data[k] = trip_content(v)
    return data


def yaml_config(path: str, apply_sys_args: bool = True):
    """
        Load yaml file , read content then parse to Dictionary.
    If thou set apply_sys_args is True.
    The arguments when thou start application will be applied to return Dictionary
        Tải tệp yaml, đọc nội dung rồi phân tích thành Từ điển.
    Nếu bạn đặt apply_sys_args là True.
    Các đối số khi bạn khởi động ứng dụng sẽ được áp dụng để trả về Từ điển
    Example: \n
        Yaml content is " my_value: value 1 " in file test.yml \n
        thou create python app looks like below: \n
            ret = yaml_config("test.yml", false) //will return {my_value:'value 1'} \n
            print(ret.my_value) \n
        and in command line exec: \n
        python my_app.py\n
        Thou will see value 1 \n
    The other case in command line exec:\n
        python my_app.py my_value='value 2' \n
        Thou will see value 2 \n
    ------------------------------------------------------------------------- \n

    Example: \n
        Yaml content is " my_value: value 1 "
        call yaml_config(..., false) will return {my_value:'value 1'}

    :param path:
    :param apply_sys_args:
    :return:
    """
    ret = cy_kit_x.yaml_config(path, apply_sys_args)
    if hasattr(cy_kit_x, "trip_content"):
        ret = cy_kit_x.trip_content(ret)
    else:
        ret = trip_content(ret)
    return ret


def combine_agruments(data):
    """
    Get all arguments when thou start python App and apply to data \n
    Example: \n
    ret = combine_agruments({a:1}) \n
    Will return {a:1} if thou start App without args \n
    And return {a:1,b:2} if thou start App with args is b=1
    ----------------------------------------------------------\n
    Nhận tất cả các đối số khi bạn khởi động Ứng dụng python và áp dụng cho dữ liệu \n
    Ví dụ: \n
    ret = Combine_agruments({a:1}) \n
    Sẽ trả về {a:1} nếu bạn khởi động Ứng dụng mà không có đối số \n
    Và trả về {a:1,b:2} nếu bạn khởi động Ứng dụng với args is b=1
    :param data:
    :return:
    """
    ret = cy_kit_x.combine_agruments(data)
    if hasattr(cy_kit_x, "trip_content"):
        ret = cy_kit_x.trip_content(ret)
    else:
        ret = trip_content(ret)
    return ret


def inject(cls: T) -> T:
    return cy_kit_x.inject(cls)


def singleton(cls: T) -> T:
    """
        Create singleton if Class \n
        Example: \n
            a = cy_kit.singleton(A) \n
            b = cy_kit.singleton(A) \n
            print(a==b) //'true' \n
    --------------------------- \n
    Example:
    class A:
        def hello():
            print ('Hello my name is "A"')
    class B:
        def hello():
            print ('Hello my name is "B"')
    the first code bellow:
        a = cy_kit.singleton(A)
        a.hello() // thou will see Hello my name is "A"
    the second code bellow
        cy_kit.config_provider(
            from_class=A,
            implement_class = A

        )
        a = cy_kit.singleton(A)
        a.hello() // thou will see Hello my name is "B"
    :param cls:
    :return:
    """
    return cy_kit_x.singleton(cls)


def scope(cls: T) -> T:
    return cy_kit_x.scope(cls)


def thread_makeup():
    return cy_kit_x.thread_makeup()


def get_local_host_ip():
    return cy_kit_x.get_local_host_ip()


def create_logs(log_dir: str, name: str):
    """
    Create log file
    :param log_dir: where log locate? this is full path tio dir
    :param name: sub folder in log_dir. where log.txt will be located
    :return:
    """
    return cy_kit_x.create_logs(log_dir, name)


def get_runtime_type(injector_instance):
    """
    If thou create an instance of Class by calling cy_kit.singleton. The real Type of instance could be changed at runtime
    To determine a real Type of Instance call this method
    ----------------------------------------------------\n
    Nếu bạn tạo một thể hiện của Lớp bằng cách gọi cy_kit.singleton. Loại phiên bản thực có thể được thay đổi trong thời gian chạy
    Để xác định Loại trường hợp thực, hãy gọi phương thức này
    :param injector_instance:
    :return:
    """

    return cy_kit_x.get_runtime_type(injector_instance)


def singleton_from_path(injector_path: str):
    """

    :param injector_path: <module>:<class name>
    :return:
    """
    return cy_kit_x.singleton_from_path(injector_path)


def to_json(data):
    return cy_kit_x.to_json(data)


def clean_up():
    try:
        cy_kit_x.clean_up()
    except Exception as e:
        pass


Graceful_Application = cy_kit_x.Graceful_Application

loop_process = cy_kit_x.loop_process
sync_call = cy_kit_x.sync_call
watch_forever = cy_kit_x.watch_forever
"""
    This decoration will make up a function run in thread.
    The inner wrapper function must return a tuple of (Function, Function) in which:
        The first function in return values use for time checking. It looks like this:
            def check()->bool:
                return datetime.datetime.now().day()==2
        The second function in return values use for forever looping routine
            while True:
                if check():
                    ... The second function call here
    Full example:
        @cy_kit.watch_forever(sleep_time=1)
        def my_run(seconds: int):
            start_time = datetime.datetime.now()
            data = dict(count=0)
            print(f"Start at ={start_time}")
            print(f"This is the demonstrated how to print 'Hello!' in every 5 second")
        
            def check(data):
                return datetime.datetime.now().second % seconds == 0
        
            def run(data):
                global count
                count = data["count"]
                count+=1
                data["count"]=count
                print(f"Hello. This is {count} is say")
        
            return data, check, run
"""
from cy_kit  import config_utils
convert_env_to_dict =  config_utils.convert_env_to_dict
