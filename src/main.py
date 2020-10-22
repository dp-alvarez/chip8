from time import sleep
import re
import pygame as pyg
from colors import *


class Cpu:
	def __init__(self):
		self.mem = memoryview(bytearray(4096))
		self.inst_size = 2
		self.ip = 0x200
		self.v = [0] * 16
		self.i = 0
		self.delay = 0
		self.event = {k:False for k in range(0xf+1)}
		self.screen_arr = [[0]*64 for _ in range(32)]
		self.init_table()
		with open("roms/octo_demo/compiled.ch8", 'rb') as f:
			f.readinto(self.mem[self.ip:])

	def init_table(self):
		table = {
			'1...': self.opcode_1nnn,
			'3...': self.opcode_3xnn,
			'6...': self.opcode_6xnn,
			'7...': self.opcode_7xnn,
			'a...': self.opcode_annn,
			'd...': self.opcode_dxyn,
			'e..1': self.opcode_exa1,
			'f.07': self.opcode_fx07,
			'f.15': self.opcode_fx15,
		}
		newtable = dict()
		for regex,opcode in table.items():
			newtable[re.compile(regex)] = opcode
		self.table = newtable

	def opcode_lookup(self, opcode):
		for regex in self.table:
			if regex.fullmatch(opcode):
				return self.table[regex]
		return None

	def tick(self):
		ret = True
		inst = self.mem[self.ip:self.ip+self.inst_size]
		inst_str = inst.hex()
		self.b1 = inst[0]
		self.b1h = self.b1 >> 4
		self.b1l = self.b1 & 0xf
		self.b2 = inst[1]
		self.b2h = self.b2 >> 4
		self.b2l = self.b2 & 0xf
		print(inst_str)

		opcode = self.opcode_lookup(inst_str)
		if opcode is not None:
			opcode()
		else:
			ret = False

		self.ip += self.inst_size
		print([hex(x) for x in self.v])
		print(hex(self.i))
		print(self.delay)
		print(hex(self.ip))
		print()
		return ret

	def opcode_1nnn(self):
		self.ip = (self.b1l << 8) + self.b2
		self.ip -= self.inst_size

	def opcode_3xnn(self):
		if self.v[self.b1l] == self.b2:
			self.ip += self.inst_size

	def opcode_6xnn(self):
		self.v[self.b1l] = self.b2

	def opcode_7xnn(self):
		n = self.v[self.b1l] + self.b2
		self.v[self.b1l] = n % 256

	def opcode_annn(self):
		self.i = (self.b1l << 8) + self.b2

	def opcode_dxyn(self):
		y = self.v[self.b2h]
		addr = self.i
		for _ in range(self.b2l):
			x = self.v[self.b1l]
			for xx in range(8):
				b = bin(self.mem[addr])[2:]
				b = '0' * (8 - len(b)) + b
				b = b[xx] == '1'
				self.screen_arr[y][x] = self.screen_arr[y][x] ^ b
				x += 1
			y += 1
			addr += 1

	def opcode_exa1(self):
		if not self.event[self.v[self.b1l]]:
			self.ip += self.inst_size

	def opcode_fx07(self):
		self.v[self.b1l] = self.delay

	def opcode_fx15(self):
		self.delay = self.v[self.b1l]


def main():
	pyg.init()
	pyg.fastevent.init()
	screen = pyg.display.set_mode((800, 600))
	pyg.display.set_caption("CHIP8 Emu")

	cpu = Cpu()

	running = True
	while running:
		cpu.delay = 0
		running = cpu.tick()

		size = 12
		screen.fill(Colors.black)
		for y in range(len(cpu.screen_arr)):
			for x in range(len(cpu.screen_arr[y])):
				if cpu.screen_arr[y][x]:
					pyg.draw.rect(screen, Colors.white, ((x*size,y*size), (size,size)), False)
		for y in range(len(cpu.screen_arr)+1):
			pyg.draw.line(screen, Colors.blue, (0,y*size), (800,y*size), 1)
			for x in range(len(cpu.screen_arr[0])+1):
				pyg.draw.line(screen, Colors.blue, (x*size,0), (x*size,600), 1)
		pyg.display.update()

		input_table = {
			pyg.K_1: 0x1,
			pyg.K_2: 0x2,
			pyg.K_3: 0x3,
			pyg.K_4: 0xc,
			pyg.K_q: 0x4,
			pyg.K_w: 0x5,
			pyg.K_e: 0x6,
			pyg.K_r: 0xd,
			pyg.K_a: 0x7,
			pyg.K_s: 0x8,
			pyg.K_d: 0x9,
			pyg.K_f: 0xe,
			pyg.K_z: 0xa,
			pyg.K_x: 0x0,
			pyg.K_c: 0xb,
			pyg.K_v: 0xf
		}
		pressed = pyg.key.get_pressed()
		for k,c in input_table.items():
			cpu.event[c] = bool(pressed[k])

		for e in pyg.fastevent.get():
			if e.type == pyg.QUIT:
				running = False
				break

	pyg.quit()


if __name__ == "__main__":
	main()
