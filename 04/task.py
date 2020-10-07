import io
import gzip
import bz2
import random

#1
#a
def capwords(str, sep=None):
	merger = sep
	if sep is None:
		merger = ' '
	str = merger.join([x.capitalize() for x in str.split(sep=sep)])
	return str

assert capwords("foo,bar boo,", sep=",") == 'Foo,Bar boo,'
assert capwords(" foo  \nbar\n") == 'Foo Bar'
# capwords("foo,bar boo,", sep="")

#b
def cut_suffix(orig, templ):
	res = orig
	if orig.endswith(templ):
		res = orig.replace(templ, '')
	return res

assert cut_suffix("foobar", "bar") == 'foo'
assert cut_suffix("foobar", "boo") == 'foobar'

#c
def boxed(orig, fill, pad):
	res = (len(orig) + 2 + 2 * pad) * fill + '\n'
	res = res + ' '.join([pad * fill, orig, pad * fill]) + '\n'
	res = res + (len(orig) + 2 + 2 * pad) * fill
	return res

assert boxed("Hello world", fill="*", pad=2) == '''\
*****************
** Hello world **
*****************'''
assert boxed("Fishy", fill="#", pad=1) == '''\
#########
# Fishy #
#########'''

#d
def find_all(orig, templ):
	return [i for (i, x) in enumerate(orig) if str.find(orig, templ, i) == i]

assert find_all("abracadabra", "a") == [0, 3, 5, 7, 10]
assert find_all("arara", "ara") == [0, 2]

#e
def common_prefix(*strs):
	cmp_str = strs[0]
	res = ''
	for i in range(len(cmp_str)):
		cur_s = cmp_str[:i + 1]
		for s in strs:
			if not s.startswith(cur_s):
				break
		else:
			res = cur_s
	return res

assert common_prefix("abrasive", "abracadabra", "abra") == 'abra'
assert common_prefix("abra", "abracadabra", "abrasive") == 'abra'
assert common_prefix("abra", "foobar") == ''

#2
#a
def reader(file_path, mode='rt', encoding=None):
	if file_path.endswith(('.gz', '.tgz')):
		return gzip.open(file_path, mode=mode, encoding=encoding)
	if file_path.endswith('.bz2'):
		return bz2.open(file_path, mode=mode, encoding=encoding)
	return open(file_path, mode=mode, encoding=encoding)

assert str(reader("./example.txt")) == '''<_io.TextIOWrapper name='./example.txt' mode='rt' encoding='UTF-8'>'''
assert str(reader("./example.txt.gz", mode="rt", encoding="ascii")) == '''<_io.TextIOWrapper name='./example.txt.gz' encoding='ascii'>'''
assert str(reader("./example.txt.bz2", mode="wb")).startswith('<bz2.BZ2File object at ')

#b
def parse_shebang(script_path):
	shebang = None
	with open(script_path) as script:
		first_line = script.readlines()[0]
		if first_line.startswith('#!'):
			shebang = first_line.replace('#!', '').strip()
		return shebang

assert parse_shebang("./script.sh") == '/bin/sh'
assert parse_shebang("./script.py") == '/usr/bin/env python3 -v'

#3
#a
def words(file):
	res = []
	for line in file:
		res += line.split(' ')
	handle.seek(0)
	return res

handle = io.StringIO("""Ignorance is the curse of God;
knowledge is the wing wherewith we fly to heaven.""")
language = words(handle)
assert language == ['Ignorance', 'is', 'the', 'curse', 'of', 'God;\n', 'knowledge', 'is', 'the', 'wing', 'wherewith', 'we', 'fly', 'to', 'heaven.']

#b
def transition_matrix(words):
	d = {}
	for i in range(1, len(words) - 1):
		u_word, v_word = words[i - 1], words[i]
		if (u_word, v_word) not in d:
			d[(u_word, v_word)] = []
		d[(u_word, v_word)].append(words[i + 1])
	return d

m = transition_matrix(language)
assert m['is', 'the'] == ['curse', 'wing']

#c
def markov_chain(language, transitions, n_words):
	rand_sentence = random.choices(language, k=2)
	for i in range(2, n_words):
		u, v = rand_sentence[i - 2], rand_sentence[i - 1]
		if (u, v) not in transitions:
			w = random.choice(language)
		else:
			w = random.choice(transitions[(u, v)])
		rand_sentence.append(w)
		u, v = v, w
	return rand_sentence

# print(markov_chain(language, m, 10))

#d
def snoop_says(file, n_words):
	with open(file, encoding='UTF-8') as snoop_file:
		language = words(snoop_file)
	transitions = transition_matrix(language)
	return markov_chain(language, transitions, n_words)

# print(snoop_says("./snoopdogg279.txt", 23))