class A:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
class B:
    def __init__(self, name):
        self.name = name

    def __enter__(self, outer_obj=None):  # Receives the outer object (instance of A)
        self.outer_obj = outer_obj  # Store the outer object for later use
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def do_something(self):
        print(f"Accessing name from outer object: {self.outer_obj.name}")

with A("Outer") as a:
    with B("Inner") as b:
        b.do_something()