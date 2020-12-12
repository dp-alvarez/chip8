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


opcode_handlers = {
	'00e0': opcode_00e0,
	'00ee': opcode_00ee,
	'1...': opcode_1nnn,
	'2...': opcode_2nnn,
	'3...': opcode_3xnn,
	'4...': opcode_4xnn,
	'5..0': opcode_5xy0,
	'6...': opcode_6xnn,
	'7...': opcode_7xnn,
	'8..0': opcode_8xy0,
	'8..1': opcode_8xy1,
	'8..2': opcode_8xy2,
	'8..3': opcode_8xy3,
	'8..4': opcode_8xy4,
	'8..5': opcode_8xy5,
	'8..6': opcode_8xy6,
	'8..7': opcode_8xy7,
	'8..e': opcode_8xye,
	'9..0': opcode_9xy0,
	'a...': opcode_annn,
	'b...': opcode_bnnn,
	'c...': opcode_cxnn,
	'd...': opcode_dxyn,
	'e.9e': opcode_ex9e,
	'e.a1': opcode_exa1,
	'f.07': opcode_fx07,
	'f.0a': opcode_fx0a,
	'f.15': opcode_fx15,
	'f.18': opcode_fx18,
	'f.1e': opcode_fx1e,
	'f.29': opcode_fx29,
	'f.33': opcode_fx33,
	'f.55': opcode_fx55,
	'f.65': opcode_fx65
}


char_data = {
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


def attach():
	import cpu
	cpu.Cpu.char_data = char_data
	cpu.Cpu.opcode_handlers = opcode_handlers
