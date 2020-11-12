import re


class Cpu:
	def __init__(self, mem, delay, screen, keyboard):
		self.mem = mem
		self.delay = delay
		self.screen = screen
		self.keyboard = keyboard
		self.opcode_size = 2
		self.ip = 0x200
		self.v = [0] * 16
		self.i = 0
		self.init_opcode_handlers()


	def init_opcode_handlers(self):
		# pylint: disable=assignment-from-no-return
		self.opcode_handlers = dict()
		for regex,opcode in Cpu.opcode_handlers.items():
			self.opcode_handlers[re.compile(regex)] = opcode.__get__(self, self.__class__)


	def opcode_lookup(self, opcode_str):
		for regex in self.opcode_handlers:
			if regex.fullmatch(opcode_str):
				return self.opcode_handlers[regex]

		raise EmulationError(f"No handler for opcode: {opcode_str}")


	def tick(self):
		self.opc = self.mem[self.ip:self.ip+self.opcode_size]
		opcode_str = self.opc.hex()
		self.opc = tuple(Byte(b) for b in self.opc)

		opcode = self.opcode_lookup(opcode_str)
		try:
			opcode()
		except EmulationError:
			raise
		except Exception as e:
			raise EmulationError(e) from e

		# print(opcode_str)
		# print([hex(x) for x in self.v])
		# print(hex(self.i))
		# print(self.delay)
		# print(hex(self.ip))
		# print()


	def opcode_1nnn(self):
		self.ip = (self.opc[0][0] << 8) + self.opc[1]

	def opcode_3xnn(self):
		if self.v[self.opc[0][0]] == self.opc[1]:
			self.ip += self.opcode_size
		self.ip += self.opcode_size

	def opcode_6xnn(self):
		self.v[self.opc[0][0]] = self.opc[1]
		self.ip += self.opcode_size

	def opcode_7xnn(self):
		n = self.v[self.opc[0][0]] + self.opc[1]
		self.v[self.opc[0][0]] = n % 256
		self.ip += self.opcode_size

	def opcode_annn(self):
		self.i = (self.opc[0][0] << 8) + self.opc[1]
		self.ip += self.opcode_size

	def opcode_dxyn(self):
		y = self.v[self.opc[1][1]]
		addr = self.i
		for _ in range(self.opc[1][0]):
			x = self.v[self.opc[0][0]]
			for xx in range(8):
				b = bin(self.mem[addr])[2:]
				b = '0' * (8 - len(b)) + b
				b = b[xx] == '1'
				self.screen[x,y] = self.screen[x,y] ^ b
				x += 1
			y += 1
			addr += 1
		self.ip += self.opcode_size

	def opcode_exa1(self):
		if not self.keyboard[self.v[self.opc[0][0]]]:
			self.ip += self.opcode_size
		self.ip += self.opcode_size

	def opcode_fx07(self):
		self.v[self.opc[0][0]] = self.delay.get()
		self.ip += self.opcode_size

	def opcode_fx15(self):
		self.delay.set(self.v[self.opc[0][0]])
		self.ip += self.opcode_size


Cpu.opcode_handlers = {
	'1...': Cpu.opcode_1nnn,
	'3...': Cpu.opcode_3xnn,
	'6...': Cpu.opcode_6xnn,
	'7...': Cpu.opcode_7xnn,
	'a...': Cpu.opcode_annn,
	'd...': Cpu.opcode_dxyn,
	'e..1': Cpu.opcode_exa1,
	'f.07': Cpu.opcode_fx07,
	'f.15': Cpu.opcode_fx15,
}


class EmulationError(Exception):
	pass


class Byte(int):
	__slots__ = tuple()

	def __new__(cls, val):
		if val < 0 or val > 255:
			raise ValueError("Value out of byte range")
		return super().__new__(cls, val)

	def __getitem__(self, index):
		if index == 0:
			return self & 0xf
		elif index == 1:
			return self >> 4
		else:
			raise IndexError("Nibble index must be 0 or 1")
