import re


class Cpu:
	def __init__(self, mem, delay, screen, keyboard):
		self.mem = mem
		self.delay = delay
		self.screen = screen
		self.keyboard = keyboard
		self.opcode_size = 2 # @todo transformar em referencia para opcode
		self.ip = 0x200
		self.v = [0] * 16
		self.i = 0
		self.init_opcode_handlers()
		self.init_chars()


	def init_opcode_handlers(self):
		# pylint: disable=assignment-from-no-return
		self.opcode_handlers = dict()
		for regex,opcode in Cpu.opcode_handlers.items():
			self.opcode_handlers[re.compile(regex)] = opcode.__get__(self, self.__class__)


	def init_chars(self):
		pos = 0
		self.char_pos = {}
		for char, data in self.char_data.items():
			data = bytes(data)
			datalen = len(data)
			pos += datalen
			self.char_pos[char] = pos
			self.mem[pos:pos+len(data)] = data


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


	def opcode_1nnn(self):
		self.ip = self.opc[1] + (self.opc[0][0] << 8)

	def opcode_3xnn(self):
		if not self.v[self.opc[0][0]] != self.opc[1]:
			self.ip += self.opcode_size
		self.ip += self.opcode_size

	def opcode_4xnn(self):
		if not self.v[self.opc[0][0]] == self.opc[1]:
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
		self.i = self.opc[1] + (self.opc[0][0] << 8)
		self.ip += self.opcode_size

	def opcode_dxyn(self):
		self.v[15] = 0
		addr = self.i
		y = self.v[self.opc[1][1]] % self.screen.shape[1]
		for _ in range(self.opc[1][0]):
			x = self.v[self.opc[0][0]] % self.screen.shape[0]
			for b in bin(self.mem[addr])[2:].rjust(8, '0'):
				b = self.screen[x,y] ^ int(b)
				self.screen[x,y] = b
				self.v[15] = self.v[15] | b
				x = (x+1) % self.screen.shape[0]
			addr += 1
			y = (y+1) % self.screen.shape[1]
		self.ip += self.opcode_size

	def opcode_ex9e(self):
		if self.keyboard[self.v[self.opc[0][0]]]:
			self.ip += self.opcode_size
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

	def opcode_fx29(self):
		char = self.v[self.opc[0][0]]
		self.i = self.char_pos[char]
		self.ip += self.opcode_size

	def opcode_fx1e(self):
		self.i = (self.i + self.v[self.opc[0][0]]) % len(self.mem)
		self.ip += self.opcode_size

	def opcode_fx55(self):
		for i in range(self.opc[0][0]+1):
			self.mem[self.i] = self.v[i]
			self.i = (self.i+1) % len(self.mem)
		self.ip += self.opcode_size

	def opcode_fx65(self):
		for i in range(self.opc[0][0]+1):
			self.v[i] = self.mem[self.i]
			self.i = (self.i+1) % len(self.mem)
		self.ip += self.opcode_size


Cpu.opcode_handlers = {
	'1...': Cpu.opcode_1nnn,
	'3...': Cpu.opcode_3xnn,
	'4...': Cpu.opcode_4xnn,
	'6...': Cpu.opcode_6xnn,
	'7...': Cpu.opcode_7xnn,
	'a...': Cpu.opcode_annn,
	'd...': Cpu.opcode_dxyn,
	'e.9e': Cpu.opcode_ex9e,
	'e..1': Cpu.opcode_exa1,
	'f.07': Cpu.opcode_fx07,
	'f.15': Cpu.opcode_fx15,
	'f.29': Cpu.opcode_fx29,
	'f.1e': Cpu.opcode_fx1e,
	'f.55': Cpu.opcode_fx55,
	'f.65': Cpu.opcode_fx65,
}


Cpu.char_data = {
	0x0: (0xF0, 0x90, 0x90, 0x90, 0xF0),
	0x1: (0x20, 0x60, 0x20, 0x20, 0x70),
	0x2: (0xF0, 0x10, 0xF0, 0x80, 0xF0),
	0x3: (0xF0, 0x10, 0xF0, 0x10, 0xF0),
	0x4: (0x90, 0x90, 0xF0, 0x10, 0x10),
	0x5: (0xF0, 0x80, 0xF0, 0x10, 0xF0),
	0x6: (0xF0, 0x80, 0xF0, 0x90, 0xF0),
	0x7: (0xF0, 0x10, 0x20, 0x40, 0x40),
	0x8: (0xF0, 0x90, 0xF0, 0x90, 0xF0),
	0x9: (0xF0, 0x90, 0xF0, 0x10, 0xF0),
	0xA: (0xF0, 0x90, 0xF0, 0x90, 0x90),
	0xB: (0xE0, 0x90, 0xE0, 0x90, 0xE0),
	0xC: (0xF0, 0x80, 0x80, 0x80, 0xF0),
	0xD: (0xE0, 0x90, 0x90, 0x90, 0xE0),
	0xE: (0xF0, 0x80, 0xF0, 0x80, 0xF0),
	0xF: (0xF0, 0x80, 0xF0, 0x80, 0x80)
}


class EmulationError(Exception):
	pass


# @todo transformar em opcode
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
