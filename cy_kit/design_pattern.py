def singleton():
    def wrapper(cls):
        setattr(cls,"__instance__",None)
        setattr(cls, "__ready_instance__", False)
        old_new = getattr(cls,"__new__")
        setattr(cls, "__new__before_wrapper__", old_new)
        old_init = getattr(cls,"__init__")
        def new_init(obj,*args, **kwargs):
            if not cls.__ready_instance__:
                old_init(obj,*args, **kwargs)
                cls.__ready_instance__ = True
        def new_new(_cls, *args, **kwargs):
            if not _cls.__instance__:
                _cls.__instance__ = super(cls, _cls).__new__(_cls)

            return _cls.__instance__

        setattr(cls,"__new__",new_new)
        setattr(cls, "__init__", new_init)

        return cls
    return wrapper