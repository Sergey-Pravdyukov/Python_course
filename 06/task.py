#1
#a

def peel(cls):
	return {attr for attr in dir(cls) if not attr.startswith('_')}

class AbstractBase:
	def some_method(self):
		pass

class Base(AbstractBase):
	def some_other_method(self):
		pass

class Closeable(Base):
	def close(self):
		pass

assert peel(Closeable) == {"some_method", "some_other_method", "close"}

#b
import functools

def implements(interface, implementation=None):
	if implementation is None:
		return functools.partial(implements, interface)
	
	api_attrs = peel(interface)
	impl_attrs = peel(implementation)
	assert api_attrs == impl_attrs, f'method(s) {api_attrs | impl_attrs} not implemented'

class Closeable:
	def close(self):
		pass

@implements(Closeable)
class FileReader:
	# ...
	def close(self):
		self.file.close()

# @implements(Closeable)
# class Noop:
# 	pass

#2
#a

class Expr:
	def __call__(self, **env):
		pass

	def d(self, wrt):
		pass

	def eq(self, other):
		pass

	def __pos__(self):
		return self

	def __neg__(self):
		return self * C(-1)

	def __add__(self, other):
		return Sum(self, other)

	def __sub__(self, other):
		return self + (-other)

	def __mul__(self, other):
		return Product(self, other)

	def __truediv__(self, other):
		return Fraction(self, other)

	def __pow__(self, other):
		return Power(self, other)

class C(Expr):
	def __init__(self, const):
		self.const = const

	def __call__(self, **env):
		return self.const

	def __repr__(self):
		return f'Const({self.const})'

	def __str__(self):
		return str(self.const)

	def d(self, wrt):
		return C(0)

	@property
	def is_constexpr(self):
		return True

	@property
	def simplified(self):
		return self.const

class V(Expr):
	def __init__(self, var):
		self.var = var

	def __call__(self, **env):
		return env[self.var]

	def __eq__(self, other):
		if not isinstance(self, type(other)):
			return False
		return self.var == other.var

	def __repr__(self):
		return f'Var(\'{self.var}\')'

	def __str__(self):
		return self.var

	def d(self, wrt):
		if self == wrt:
			return C(1)
		return C(0)

	@property
	def is_constexpr(self):
		return False

	@property
	def simplified(self):
		return self
	

assert C(42)() == 42
assert C(42).d(V("x"))() == 0
assert V('x')(x=42) == 42
assert V("x").d(V("x"))() == 1
assert V("x").d(V("y"))() == 0

# b
class BinOp(Expr):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
    	return f'{type(self).__name__}({self.lhs.__repr__()}, {self.rhs.__repr__()})'

    def __str__(self):
    	return f'({self.token} {self.lhs.__str__()} {self.rhs.__str__()})'

    def __call__(self, **env):
    	return self.__class__.operation(self.lhs(**env), self.rhs(**env))

    @property
    def is_constexpr(self):
    	return self.lhs.is_constexpr and self.rhs.is_constexpr

    @property
    def simplified(self):
    	if self.is_constexpr:
    		return C(self())
    	return self.__class__(self.lhs.simplified, self.rhs.simplified)
    	

class Sum(BinOp):
	token = '+'

	def operation(a, b):
		return a + b

	def d(self, wrt):
		return self.lhs.d(wrt) + self.rhs.d(wrt)

class Product(BinOp):
	token = '*'

	def operation(a, b):
		return a * b

	def d(self, wrt):
		return self.lhs.d(wrt) * self.rhs + self.lhs * self.rhs.d(wrt)

class Fraction(BinOp):
	token = '/'

	def operation(a, b):
		return a / b

	def d(self, wrt):
		return (self.lhs.d(wrt) * self.rhs - self.lhs * self.rhs.d(wrt)) / \
		(self.rhs * self.rhs)

x = V("x")
c = C(5)
assert Sum(x, c)(x=42) == 47 
assert Sum(x, Product(x, x)).d(x)(x=42) == 85
assert Product(x, Sum(x, C(2)))(x=42) == 1848
assert Sum(x, x).d(x)(x=42) == 2
assert Sum(x, c).d(x)(x=42) == 1
assert Sum(c, x).d(x)(x=42) == 1
assert Sum(c, c).d(x)(x=42) == 0
assert Product(x, Sum(x, x)).d(x)(x=42) == 168
assert Product(x, Product(x, x)).d(x)(x=42) == 5292
assert abs(Fraction(Product(x, V("y")), Sum(C(42), x)).d(x)(x=42, y=24) - 0.14285) < 1e-5
assert Fraction(Product(x, V("y")), Sum(C(42), x)).d(V("y"))(x=42, y=24) == 0.5

#c
class Power(BinOp):
	token = '**'

	def operation(a, b):
		return a ** b

	def d(self, wrt):
		return self.rhs * (self.lhs ** (self.rhs - C(1))) * self.lhs.d(wrt)

assert abs(Power(Fraction(x, C(4)), Sum(C(2), C(2)))(x=42) - 12155.0625) <= 1e-4
assert abs(Power(Fraction(x, C(4)), Sum(C(2), C(2))).d(x)(x=42) - 1157.625) <= 1e-3

#d
assert Power(Fraction(x, C(4)), Sum(C(2), C(2))).__str__() == '(** (/ x 4) (+ 2 2))'
assert Sum(x, Product(x, x)).d(x).__str__() == '(+ 1 (+ (* 1 x) (* x 1)))'
assert Product(x, Sum(x, C(2))).__str__() == '(* x (+ x 2))'
assert Power(Fraction(x, C(4)), C(2)).__str__() == '(** (/ x 4) 2)' 

#3
#a
assert ((C(1) - x)**C(3) + x).__str__() == '(+ (** (+ 1 (* x -1)) 3) x)'

#b
def newton_raphson(expr, x0, eps):
	cur_x = x0
	
	def iteration(f, x):
		return x - f(x=x) / f.d(V('x'))(x=x)

	next_x = iteration(expr, x0)

	while abs(next_x - cur_x) >= eps:
		cur_x = next_x
		next_x = iteration(expr, cur_x)

	return cur_x

expr = (V("x") + C(-1))**C(3) + V("x")
zero = newton_raphson(expr, 0.5, eps=1e-4)
assert expr.__str__() == '(+ (** (+ x -1) 3) x)'
assert abs(zero - 0.31767219617165293) <= 1e-6
assert abs(expr(x=zero)) <= 1e-5 

#4
#a
assert (V("x") + C(1)).is_constexpr == False
assert (C(1) + C(42) * V("x")).d(V("x")).is_constexpr == False
assert (C(1) + C(42) * C(2)).is_constexpr == True

#b

assert str((C(1) + C(42) * C(2)).simplified) == '85'
assert str((C(1) * V("y") + C(42) * C(2) / V("x")).simplified) == '(+ (* 1 y) (/ 84 x))'










