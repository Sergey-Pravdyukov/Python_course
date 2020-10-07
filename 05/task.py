from collections import *
import functools
from graphviz import Graph

#1
#a
def factor(seq):
	Factor = namedtuple('Factor', ['elements', 'levels'])

	Factor.levels = defaultdict(int)
	Factor.elements = []
	level = -1
	for elem in seq:
		level += int(Factor.levels.setdefault(elem, level + 1) == level + 1)
		Factor.elements.append(Factor.levels[elem])
	
	return Factor

f = factor(["a", "a", "b"])
assert f.elements == [0, 0, 1]
assert f.levels["b"] == 1
assert list(f.levels.items()) == [('a', 0), ('b', 1)]
f = factor(["a", "b", "c", "b", "a"])
assert f.elements == [0, 1, 2, 1, 0]
assert list(f.levels.items()) == [('a', 0), ('b', 1), ('c', 2)]

#b
def group_by(seq, f):
	d = defaultdict(list)
	for elem in seq:
		d[f(elem)].append(elem)
	return d

assert group_by(["foo", "boo", "barbra"], len) == {3: ['foo', 'boo'], 6: ['barbra']}

#c 
def invert(d):
	d_inv = defaultdict(set)
	for k, v in d.items():
		d_inv[v].add(k)
	return d_inv

assert dict(invert({"a": 42, "b": 42, "c": 24})) == {24: {'c'}, 42: {'b', 'a'}}

#2
#a
def lru_cache(f=None, maxsize=64):
	if f is None:
		return functools.partial(lru_cache, maxsize=maxsize)

	CacheInfo = namedtuple('CacheInfo', ['hits', 'misses', 'maxsize', 'currsize'])

	hits, misses, currsize = 0, 0, 0
	cache = OrderedDict()

	@functools.wraps(f)
	def inner(*args, **kwargs):
		nonlocal hits, misses, currsize, cache

		key = (args, *tuple(kwargs))

		if key not in cache:
			cache[key] = f(*args, **kwargs)
			misses += 1
		else:
			hits += 1
		
		if currsize >= maxsize:
			cache.popitem(last=False)
		currsize = len(cache.items())

		return cache[key]

	def clear_cache():
		nonlocal hits, misses, currsize, cache
		hits, misses, currsize = 0, 0, 0
		cache = OrderedDict()
		print(cache)

	inner.cache_info = lambda : CacheInfo(hits, misses, maxsize, currsize)
	inner.clear_cache = lambda : clear_cache()
	inner.get_cache = lambda : cache
	return inner

@lru_cache(maxsize=5)
def fib(n):
	return n if n <= 1 else fib(n - 1) + fib(n - 2)

assert fib(10) == 55
# fib.clear_cache()
# print(fib.cache_info())

#3
#a
def build_graph(words, mismatch_percent):
	def hamming_dist(u, v):	
		counter = 0
		for i in range(len(u)):
			counter += int(u[i] != v[i])
		return counter

	n = len(words)
	hamming_graph = defaultdict(list)
	for u_id, u_word in enumerate(words):
		hamming_graph.setdefault(u_id, [])
		for v_id, v_word in enumerate(words):
			is_same_len = len(u_word) == len(v_word)
			if is_same_len and hamming_dist(u_word, v_word) <= mismatch_percent * n / 100 and u_id != v_id:
				hamming_graph[u_id].append(v_id)
	return hamming_graph

words = ["hello", "helol", "ehllo", "tiger", "field"]
g = build_graph(words, mismatch_percent=50.)
assert dict(g.items()) == {0: [1, 2], 1: [0], 2: [0], 3: [], 4: []}

#b
def export_graph(g, labels):
	graph = Graph()
	for (g_node, g_edges), label in list(zip(g.items(), labels)):
		graph.node(str(g_node), label)
		all_edge_pairs = map(lambda adj_node: str(g_node) + str(adj_node), g_edges)
		graph.edges(list(filter(lambda edge: edge[0] < edge[1], all_edge_pairs)))
	return graph

g = {0: [1, 2], 1: [0], 2: [0]}
labels = ["a", "b", "c"]
assert export_graph(g, labels).source == '''\
graph {
	0 [label=a]
	0 -- 1
	0 -- 2
	1 [label=b]
	2 [label=c]
}'''

#c
def find_connected_components(g):
	used = [False] * len(g)
	connected_components = []

	def dfs(u, connected_component):
		used[u] = True
		connected_component.add(u)
		for v in g[u]:
			if not used[v]:
				dfs(v, connected_component)

	for node in g:
		if not used[node]:
			connected_component = set()
			dfs(node, connected_component)
			connected_components.append(connected_component)
	
	return connected_components 

g = {0: [1, 2], 1: [0], 2: [0], 3: [], 4: []}
assert find_connected_components(g) == [{0, 1, 2}, {3}, {4}]

#d
def find_consensus(words):
	n = len(words[0])
	consensus_letters = []
	for i in range(n):
		letters = list(map(lambda word: word[i], words)) 
		consensus_letters.append(max(set(letters), key=letters.count))
	return ''.join(consensus_letters)

assert find_consensus(["hello", "helol", "ehllo"]) == 'hello'
assert find_consensus(["bug", "bow", "bag", "bar"]) == 'bag'

#e 
def correct_typos(words, mismatch_percent):
	hamming_graph = dict(build_graph(words, mismatch_percent).items())
	connected_components = find_connected_components(hamming_graph)
	for connected_component in connected_components:
		connected_words = [words[i] for i in list(connected_component)] 
		consenus_word = find_consensus(connected_words)
		for idx, word in enumerate(words):
			if idx in connected_component:
				words[idx] = consenus_word
	return words

words = ["hello", "helol", "ehllo", "tiger", "field", "abracadabra"]
assert correct_typos(words, mismatch_percent=50.) == ['hello', 'hello', 'hello', 'tiger', 'field', 'abracadabra']





