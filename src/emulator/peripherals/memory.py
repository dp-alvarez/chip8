class Memory:
	def __new__(cls, size):
		ret = memoryview(bytearray(size))
		return ret
