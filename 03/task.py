from functools import reduce, partial, wraps

# task 1
# a
def union(*sets):
	return reduce(lambda x, y: x | y, sets)

assert union({1, 2, 3}, {10}, {2, 6}) == {1, 2, 3, 6, 10}
assert union({1, 2, 3}, {10}, {2, 6}, set(), {1}) == {1, 2, 3, 6, 10}

#b
def digits(n):
	if n == 0:
		return [0]
	result = []
	while n != 0:
		result.append(n % 10)
		n //= 10
	return list(reversed(result))

assert digits(0) == [0]
assert digits(1914) == [1, 9, 1, 4]

#c
def lcm(*nums):
	def gcd_of_two(x, y):
		while y:
			x, y = y, x % y
		return x

	def lcm_of_two(x, y):
		return x * y // gcd_of_two(x, y)

	return reduce(lambda x, y: lcm_of_two(x, y), nums)

assert lcm(100500, 42) == 703500
assert lcm(*range(2, 40, 8)) == 19890

#d
def compose(*funcs):
	return reduce(lambda f, g: lambda x: f(g(x)), funcs)

f = compose(lambda x: 2 * x, lambda x: x + 1, lambda x: x % 9)
assert f(42) == 14


#2
#a
def once(f):
	called = False
	res = None

	def inner(*args, **kwargs):
		nonlocal called
		nonlocal res
		if not called:
			called = True
			res =  f(*args, **kwargs)
		return res

	return inner

@once
def initialize_settings():
    print("Settings initialized.")
    return {"token": 42}

assert initialize_settings() == {"token": 42}
assert initialize_settings() == {"token": 42}
assert initialize_settings() == {"token": 42}

#b
def trace_if(pred):
	def deco(f):

		@wraps(f)
		def inner(*args, **kwargs):
			result = f(*args, **kwargs)
			if pred(*args, **kwargs) == True:
				args_str = [str(args)[:-1]]
				kwargs_str = [f'{k}={v}' for k, v in kwargs.items()]
				params = ', '.join(args_str + kwargs_str) + ')'
				print(f'{f.__name__}{params} = ...')
				print(f'{f.__name__}{params} = {result}')
			return result
		return inner
	return deco	

@trace_if(lambda x, y, **kwargs: kwargs.get("integral"))
def div(x, y, integral=False):
	return x // y if integral else x / y

assert div(4, 2) == 2.0
assert div(4, 2, integral=True) == 2

#c
def n_times(n, f=None):
	if f is None:
		return partial(n_times, n)

	@wraps(f)
	def inner(*args, **kwargs):
		for _ in range(n):
			f(*args, **kwargs)

	return inner

@n_times(3)
def do_something():
	print("Something is going on!")

do_something()

#3
#a
def project():
	tasks = []
	dependencies = {}
	called_dependencies = set()		

	def register(f=None, depends_on=[]):
		if f is None:
			return partial(register, depends_on=depends_on)

		nonlocal tasks
		nonlocal dependencies
		
		if not f is None:
			tasks.append(f.__name__)
		
		if f.__name__ not in dependencies:
			dependencies[f.__name__] = []
		dependencies[f.__name__] += depends_on

		@wraps(f)
		def inner():
			for dependency in dependencies[f.__name__]:
				if dependency not in called_dependencies:
					called_dependencies.add(dependency)
					dep_f = globals().get(dependency)
					dep_f()
			f()

		inner.get_dependencies = lambda : dependencies[f.__name__]
		return inner

	register.get_all = lambda : tasks
	return register

register = project()
@register
def do_something():
	print("doing something")

# @register(depends_on=["do_something"])
@register(depends_on=["do_something"])
def do_other_thing():
	print("doing other thing")

assert register.get_all() == ['do_something', 'do_other_thing']
# do_something()
# do_other_thing()

#b
assert do_something.get_dependencies() == []
assert do_other_thing.get_dependencies() == ['do_something']

#c
# do_something()
# do_other_thing()

register = project()
@register
def task_a():
	print("task_a")

@register(depends_on=["task_a"])
def task_b():
	print("task_b")

@register(depends_on=["task_a"])
def task_c():
	print("task_c")

@register(depends_on=["task_b", "task_c"])
def task_d():
	print("task_d")

task_d()