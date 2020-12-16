class Opcode(bytes):
	__slots__ = tuple()
	size = 2

	def __new__(cls, val):
		return super().__new__(cls, val[0:cls.size])

	def __getitem__(self, index):
		if isinstance(index, slice):
			start, stop, _ = index.indices(2*self.size)
			ret = 0
			for i,index in enumerate(reversed(range(start, stop))):
				ret += self.nibble(index) << (4*i)
			return ret
		else:
			return self.nibble(index)

	def nibble(self, index):
		byte, index = divmod(index, 2)
		byte = super().__getitem__(byte)
		if index == 0:
			return byte >> 4
		else:
			return byte & 0xf

	def __str__(self):
		return self.hex()
