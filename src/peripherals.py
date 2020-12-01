import itertools
import numpy as np
import collections.abc


class Memory:
	def __new__(cls, size):
		ret = memoryview(bytearray(size))
		return ret


class Screen:
	def __init__(self, size):
		self.shape = tuple(size[0:2])
		self.data = np.zeros(self.shape, dtype='bool')

	def __getitem__(self, index):
		return self.data[index]

	def __setitem__(self, index, value):
		self.data[index] = bool(value)

	def __iter__(self):
		return np.ndindex(*self.shape)


class Keyboard(collections.abc.Mapping):
	def __init__(self, nkeys):
		self.data = {key:False for key in range(nkeys)}

	def __getitem__(self, key):
		return self.data[key]

	def __setitem__(self, key, value):
		if key not in self.data:
			raise KeyError(f"Invalid key: {key}")
		self.data[key] = bool(value)

	def __len__(self):
		return len(self.data)

	def __iter__(self):
		return iter(self.data)

	def items(self):
		return self.data.items()


class Delay:
	def __init__(self, freq):
		self.freq = freq
		self.data = 0
		self.last_update = None

	def set(self, value):
		self.data = value

	def get(self):
		return self.data

	def tick(self, time):
		if self.last_update is None or time-self.last_update >= self.freq:
			if self.data > 0:
				self.data -= 1
			self.last_update = time

	def __str__(self):
		return str(self.data)
