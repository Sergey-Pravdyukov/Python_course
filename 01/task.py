from random import choice
from itertools import combinations

def print_map(m, pos):
	rows_number, columns_number = shape(m)
	for i in range(rows_number):
		for j in range(columns_number):
			if (i, j) == pos:
				print('@', end='')
			elif m[i][j] == True:
				print('.', end='')
			elif m[i][j] == False:
				print('#', end='')
		print()

def shape(m):
	assert m, "map must be not empty"
	return len(m), len(m[0])

def neighbours(m, pos):
	deltas = [(1, 0), (0, -1), (-1, 0), (0, 1)]
	x, y = pos
	rows_number, columns_number = shape(m)
	neighbour_cells = []
	for dx, dy in deltas:
		cur_x, cur_y = x + dx, y + dy 
		is_x_inside = 0 <= cur_x <= rows_number
		is_y_inside = 0 <= cur_y <= columns_number
		if is_x_inside and is_y_inside and m[cur_x][cur_y] == True:
			neighbour_cells.append((cur_x, cur_y))
	return neighbour_cells

def find_route(m, initial):
	x, y = initial
	rows_number, columns_number = shape(m)
	is_x_on_boundary = x == 0 or x == rows_number - 1
	is_y_on_boundary = y == 0 or y == columns_number - 1
	route = [initial]
	while not (is_x_on_boundary or is_y_on_boundary): 
		x, y = choice(neighbours(m, (x, y)))
		is_x_on_boundary = x == 0 or x == rows_number - 1
		is_y_on_boundary = y == 0 or y == columns_number - 1
		route.append((x, y))
	return route

def escape(m, initial):
	route = find_route(m, initial)
	for step in route:
		print_map(m, step)
		print()

def hamming(seq1, seq2):
	diffs = 0
	for i in range(len(seq1)):
		diffs += int(seq1[i] != seq2[i])
	return diffs

def hba1(path, distance):
	with open(path) as inp_file:
		lines = list(map(lambda x: x.strip('\n'), inp_file.readlines()))

	min_dist = float('Inf')
	for ((f_id, f_str), (s_id, s_str)) in combinations(enumerate(lines), 2):
		cur_distance = distance(f_str, s_str) 
		if min_dist > cur_distance:
			min_dist = cur_distance
			min_ids = (f_id, s_id)
	return min_ids

def kmers(seq, k):
	d = {}
	subseq = seq[:k]
	for i in range(k, len(seq)):
		if subseq not in d:
			d[subseq] = 0
		d[subseq] += 1
		subseq = subseq[1:] + seq[i]
	return d

def distance1(seq1, seq2, k=2):
	d1 = kmers(seq1, k)
	d2 = kmers(seq2, k)
	a = sum([abs(d1.get(key, 0) - d2.get(key, 0)) for key in (d1.keys() | d2.keys())])
	return a

m = [[False, False, False, False],
	[False, True, False, True],
	[False, True, False, True],
	[True, True, False, False],
	[False, True, True, True]]

# print_map(m, (2, 1))
# print(shape([[True, False]]))
# print(shape(m))
# print(neighbours(m, (0, 0)))
# print(neighbours(m, (2, 1)))
# print(find_route(m, (1, 1)))
# escape(m, (1, 1))

# print(hamming("foo", "boo"))
# print(hba1('./HBA1.txt', hamming))
# print(kmers('abracadabra', 2))
# print(distance1("abracadabra", "abracadabra"))
# print(distance1("abracadabra", "anaconda"))
# print(distance1("abracadabra", "abra"))
