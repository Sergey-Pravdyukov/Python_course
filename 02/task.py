def compose(g, f):
	return lambda x: g(f(x))

# f = compose(lambda x: x**2, lambda x: x + 1)
# print(f(2))

def const(x):
	return lambda *args, **kwargs: x

# f = const(42)
# print(f())
# print(f(range(4), range(2), foo="bar"))

def flip(f):
	return lambda *args, **kwargs: f(*tuple(reversed(args)), **kwargs)

# f = flip(map)
# print(list(f(range(5), range(0, 10, 2), lambda x, y: x**y)))
# print(list(map(lambda x, y: x**y, range(0, 10, 2), range(5))))

def pow(x, p):
	return x**p

def curry(f, *args, **kwargs):
	return lambda *n_args, **n_kwargs: f(*args, *n_args, **kwargs, **n_kwargs)

# ten_pow = curry(pow, 10)
# print(ten_pow(3))
# square = curry(pow, p=2)
# print(square(42))

def enumerate(seq, start=0):
	seq = list(seq)
	return [(i + start, seq[i]) for i in range(len(seq))]

# print(list(enumerate("abcd")))
# print(list(enumerate(map(lambda ch: ch * 2, "abcd"), 1)))

def which(pred, seq):
	return [i for i in range(len(seq)) if pred(seq[i])]

# print(list(which(lambda x: x % 2 == 0, [4, 9, 15, 8, 1, 54])))

def all(pred, seq):
	seq = list(seq)
	return which(pred, seq) == list(range(len(seq)))

# print(all(lambda x: x % 2 == 0, [4, 9, 15]))
# xs = [1, 1, 2, 3, 4, 8]
# print(all(lambda p: p[0] <= p[1], zip(xs, xs[1:])))

def any(pred, seq):
	seq = list(seq)
	return which(pred, seq) != []

# print(any(lambda x: x % 2 == 0, [4, 9, 15]))
# print(any(lambda x: x % 2 == 0, []))

OK, ERROR = "OK", "ERROR"

def dot(input):
    if not input:
        return ERROR, "eof", input
    if input[0] != ".":
        return ERROR, f"expected . got `{input[0]}`", input
    return OK, ".", input[1:]

# print(dot("..."))
# print(dot("!.."))
# print(dot(""))

def char(ch):
    def inner(input):
        if not input:
            return ERROR, "eof", input
        if input[0] != ch:
            return ERROR, f"expected `{ch}` got `{input[0]}`", input
        return OK, ch, input[1:]
    return inner

# p = char("(")
# print(p("()"))

def any_of(s):
	def inner(input):
		if not input:
			return ERROR, "eof", input
		if input[0] not in s:
			return ERROR, f"expected any of `{s}`, got `{input[0]}`", input
		return OK, input[0], input[1:]
	return inner

# p = any_of("()")
# print(p("("))
# print(p(")"))
# print(p("[]"))

def chain(*parsers):
	def inner(input):
		results = []
		for parser in parsers:
			if not input:
				return ERROR, 'eof', input
			tag, result, input = parser(input)
			if tag == ERROR:
				return tag, result, input
			results.append(result)
		return OK, results, input
	return inner

# p = chain(char("("), char(")"))
# print(p("()"))
# print(p("("))
# print(p(")"))
# print(p("(("))

def choice(*parsers):
	def inner(input):
		if not input:
			return ERROR, 'eof', input
		for parser in parsers:
			tag, result, leftover = parser(input)
			if tag == OK:
				return tag, result, leftover
		return ERROR, 'none matched', input
	return inner

# p = choice(char("."), char("!"))
# print(p('.'))
# print(p('!'))
# print(p('?'))

def many(parser):
	def inner(input):
		results = []
		tag, result, leftover = parser(input)
		while tag == OK:
			results.append(result)
			tag, result, leftover = parser(leftover)
		return OK, results, leftover
	return inner

# p = many(char("."))
# print(p('...?!'))
# print(p('.'))
# print(p('I have no idea what this is.'))

def many1(parser):
	def inner(input):
		tag, result, leftover = parser(input)
		if tag == ERROR:
			return ERROR, result, leftover
		tag, results, leftover = many(parser)(leftover)
		return tag, [result, *results], leftover
	return inner

# p = many1(char("."))
# print(p(".!"))
# print(p("!!"))
# print(p(""))

def transform(p, f):
    def inner(input):
        tag, res, leftover = p(input)
        return tag, f(res) if tag == OK else res, leftover
    return inner

def sep_by(p, separator):
	def inner(input):
		tag, result, leftover = p(input)
		if tag == ERROR:
			return ERROR, result, input
		many_chain_parser = many(chain(separator, p))
		tag, results, leftover = transform(many_chain_parser, lambda xs: [x for _, x in xs])(leftover)
		if tag == ERROR:
			return ERROR, results, input
		return OK, [result, *results], leftover
	return inner

# p = sep_by(any_of("1234567890"), char(","))
# print(p("1,2,3"))
# print(p("1"))
# print(p(""))

def parse(p, input):
    tag, result, leftover = p(input)
    assert tag == OK and not leftover, (result, leftover)
    return result

lparen, rparen = char("("), char(")")
ws = many1(any_of(" \r\n\t"))
number = transform(
    many1(any_of("1234567890")),
    lambda digits: int("".join(digits))
)
op = any_of("+-*/")


def sexp(input):
    args = sep_by(choice(number, sexp), ws)

    # Уберём лишние None из результата chain.
    p = chain(lparen, op, ws, args, rparen)
    p = transform(p, lambda res: (res[1], res[3]))
    return p(input)

print(parse(sexp, "(+ 42 (* 2 4))"))