import re


class Cpu:
	def __init__(self, mem, delay, screen, keyboard, random):
		self.mem = mem
		self.delay = delay
		self.screen = screen
		self.keyboard = keyboard
		self.random = random
		self.stack = []
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
		try:
			self.opc = Opcode(self.mem[self.ip:])
			opcode = self.opcode_lookup(self.opc.hex())
			opcode()
		except EmulationError:
			raise
		except Exception as e:
			raise EmulationError(e) from e


	def __str__(self):
		ret = ""
		for i,x in enumerate(self.v):
			ret += f"{i:01X}: 0x{x:02X}"
			ret += "    " if (i+1)%4 else "\n"

		ret += f"I:  0x{self.i:04X} -"
		for addr in range(self.i, self.i+4):
			ret += f" {self.mem[addr]:02x}" if addr < len(self.mem) else " XX"
		ret += "\n"

		ret += f"IP: 0x{self.ip:04X} - {self.opc}\n"
		ret += f"Delay: {self.delay}\n"
		ret += f"Stack: {str(self.stack)}\n"

		return ret


	def opcode_00e0(self):
		for x,y in self.screen:
			self.screen[x,y] = False
		self.ip += self.opc.size

	def opcode_00ee(self):
		self.ip = self.stack.pop()
		self.ip += self.opc.size

	def opcode_1nnn(self):
		self.ip = self.opc[1:4]

	def opcode_2nnn(self):
		self.stack.append(self.ip)
		self.ip = self.opc[1:4]

	def opcode_3xnn(self):
		if not self.v[self.opc[1]] != self.opc[2:4]:
			self.ip += self.opc.size
		self.ip += self.opc.size

	def opcode_4xnn(self):
		if not self.v[self.opc[1]] == self.opc[2:4]:
			self.ip += self.opc.size
		self.ip += self.opc.size

	def opcode_5xy0(self):
		if not self.v[self.opc[1]] != self.v[self.opc[2]]:
			self.ip += self.opc.size
		self.ip += self.opc.size

	def opcode_6xnn(self):
		self.v[self.opc[1]] = self.opc[2:4]
		self.ip += self.opc.size

	def opcode_7xnn(self):
		n = self.v[self.opc[1]] + self.opc[2:4]
		self.v[self.opc[1]] = n % 256
		self.ip += self.opc.size

	def opcode_8xy0(self):
		self.v[self.opc[1]] = self.v[self.opc[2]]
		self.ip += self.opc.size

	def opcode_8xy1(self):
		self.v[self.opc[1]] = self.v[self.opc[1]] | self.v[self.opc[2]]
		self.ip += self.opc.size

	def opcode_8xy2(self):
		self.v[self.opc[1]] = self.v[self.opc[1]] & self.v[self.opc[2]]
		self.ip += self.opc.size

	def opcode_8xy3(self):
		self.v[self.opc[1]] = self.v[self.opc[1]] ^ self.v[self.opc[2]]
		self.ip += self.opc.size

	def opcode_8xy4(self):
		v = self.v[self.opc[1]] + self.v[self.opc[2]]
		carry, v = divmod(v, 256)
		self.v[self.opc[1]] = v
		self.v[15] = int(bool(carry))
		self.ip += self.opc.size

	def opcode_8xy5(self):
		v = self.v[self.opc[1]] - self.v[self.opc[2]]
		carry, v = divmod(v, 256)
		self.v[self.opc[1]] = v
		self.v[15] = int(not bool(carry))
		self.ip += self.opc.size

	def opcode_8xy6(self):
		v = self.v[self.opc[2]]
		self.v[self.opc[1]] = v >> 1
		self.v[15] = int(bool(v & 1))
		self.ip += self.opc.size

	def opcode_8xy7(self):
		v = self.v[self.opc[2]] - self.v[self.opc[1]]
		carry, v = divmod(v, 256)
		self.v[self.opc[1]] = v
		self.v[15] = int(not bool(carry))
		self.ip += self.opc.size

	def opcode_8xye(self):
		v = self.v[self.opc[2]]
		self.v[self.opc[1]] = (v << 1) % 256
		self.v[15] = int(bool(v & 128))
		self.ip += self.opc.size

	def opcode_9xy0(self):
		if not self.v[self.opc[1]] == self.v[self.opc[2]]:
			self.ip += self.opc.size
		self.ip += self.opc.size

	def opcode_annn(self):
		self.i = self.opc[1:4]
		self.ip += self.opc.size

	def opcode_bnnn(self):
		self.ip = self.v[0] + self.opc[1:4]

	def opcode_cxnn(self):
		self.v[self.opc[1]] = self.random.randrange(256) & self.opc[2:4]
		self.ip += self.opc.size

	def opcode_dxyn(self):
		col = 0
		addr = self.i
		y = self.v[self.opc[2]] % self.screen.shape[1]
		for _ in range(self.opc[3]):
			x = self.v[self.opc[1]] % self.screen.shape[0]
			for b in bin(self.mem[addr])[2:].rjust(8, '0'):
				b = bool(int(b))
				old = self.screen[x,y]
				self.screen[x,y] = self.screen[x,y] ^ b
				col += old and not self.screen[x,y]
				x = (x+1) % self.screen.shape[0]
			addr += 1
			y = (y+1) % self.screen.shape[1]
		self.v[15] = int(bool(col))
		self.ip += self.opc.size

	def opcode_ex9e(self):
		if self.keyboard[self.v[self.opc[1]]]:
			self.ip += self.opc.size
		self.ip += self.opc.size

	def opcode_exa1(self):
		if not self.keyboard[self.v[self.opc[1]]]:
			self.ip += self.opc.size
		self.ip += self.opc.size

	def opcode_fx07(self):
		self.v[self.opc[1]] = self.delay.get()
		self.ip += self.opc.size

	def opcode_fx0a(self):
		for key,status in self.keyboard.items():
			if status:
				self.v[self.opc[1]] = key
				self.ip += self.opc.size
				break

	def opcode_fx15(self):
		self.delay.set(self.v[self.opc[1]])
		self.ip += self.opc.size

	def opcode_fx18(self):
		# @todo buzzer
		self.ip += self.opc.size

	def opcode_fx1e(self):
		self.i = (self.i + self.v[self.opc[1]]) % len(self.mem)
		self.ip += self.opc.size

	def opcode_fx29(self):
		char = self.v[self.opc[1]]
		self.i = self.char_pos[char]
		self.ip += self.opc.size

	def opcode_fx33(self):
		addr = self.i
		for d in str(self.v[self.opc[1]]).rjust(3, '0'):
			self.mem[addr] = int(d)
			addr += 1
		self.ip += self.opc.size

	def opcode_fx55(self):
		for i in range(self.opc[1]+1):
			self.mem[self.i] = self.v[i]
			self.i = (self.i+1) % len(self.mem)
		self.ip += self.opc.size

	def opcode_fx65(self):
		for i in range(self.opc[1]+1):
			self.v[i] = self.mem[self.i]
			self.i = (self.i+1) % len(self.mem)
		self.ip += self.opc.size


Cpu.opcode_handlers = {
	'00e0': Cpu.opcode_00e0,
	'00ee': Cpu.opcode_00ee,
	'1...': Cpu.opcode_1nnn,
	'2...': Cpu.opcode_2nnn,
	'3...': Cpu.opcode_3xnn,
	'4...': Cpu.opcode_4xnn,
	'5..0': Cpu.opcode_5xy0,
	'6...': Cpu.opcode_6xnn,
	'7...': Cpu.opcode_7xnn,
	'8..0': Cpu.opcode_8xy0,
	'8..1': Cpu.opcode_8xy1,
	'8..2': Cpu.opcode_8xy2,
	'8..3': Cpu.opcode_8xy3,
	'8..4': Cpu.opcode_8xy4,
	'8..5': Cpu.opcode_8xy5,
	'8..6': Cpu.opcode_8xy6,
	'8..7': Cpu.opcode_8xy7,
	'8..e': Cpu.opcode_8xye,
	'9..0': Cpu.opcode_9xy0,
	'a...': Cpu.opcode_annn,
	'b...': Cpu.opcode_bnnn,
	'c...': Cpu.opcode_cxnn,
	'd...': Cpu.opcode_dxyn,
	'e.9e': Cpu.opcode_ex9e,
	'e.a1': Cpu.opcode_exa1,
	'f.07': Cpu.opcode_fx07,
	'f.0a': Cpu.opcode_fx0a,
	'f.15': Cpu.opcode_fx15,
	'f.18': Cpu.opcode_fx18,
	'f.1e': Cpu.opcode_fx1e,
	'f.29': Cpu.opcode_fx29,
	'f.33': Cpu.opcode_fx33,
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
