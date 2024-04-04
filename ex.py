import inspect

def a(x):
    "docstring"
    f = inspect.currentframe()
    print(dir(f))
    print(f.__doc__)
    print(f.f_locals)
    print(f.f_globals)
    print(f.f_trace_lines)

a(3)
