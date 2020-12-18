import itertools
import array


class Screen:
	def __init__(self, size):
		self.shape = size
		self.raw = array.array('B', bytes(self.shape[0]*self.shape[1]))
		self.data = memoryview(self.raw).cast('B', self.shape)

	def __getitem__(self, index):
		return self.data[index]

	def __setitem__(self, index, value):
		self.data[index] = bool(value)

	def __iter__(self):
		return itertools.product(range(self.shape[0]), range(self.shape[1]))
