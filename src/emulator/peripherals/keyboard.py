import collections.abc


class Keyboard(collections.abc.Mapping):
	def __init__(self, keys):
		self.data = {key:False for key in keys}

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

	def copy(self):
		ret = type(self)(self.data.keys())
		ret.data = self.data.copy()
		return ret
