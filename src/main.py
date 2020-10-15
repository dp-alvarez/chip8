from time import sleep
import re
import pygame as pyg
from colors import *


def main():
	pyg.init()
	pyg.fastevent.init()
	screen = pyg.display.set_mode((800, 600))
	pyg.display.set_caption("CHIP8 Emu")

	inst_size = 2
	ip = 0x200
	v = [0] * 16
	i = 0
	delay = 0
	delay_lastupdate = None
	screen_arr = []
	for _ in range(32):
		screen_arr.append([0]*64)
	event = 0x0
	mem = memoryview(bytearray(4096))
	with open("roms/octo_demo/compiled.ch8", 'rb') as f:
		f.readinto(mem[ip:])

	running = True
	while running:
		inst = mem[ip:ip+inst_size]
		inst_str = inst.hex()
		b1 = inst[0]
		b1h = b1 >> 4
		b1l = b1 & 0xF
		b2 = inst[1]
		b2h = b2 >> 4
		b2l = b2 & 0xF
		print(inst_str)

		if re.fullmatch('6...', inst_str):
			v[b1l] = b2
		elif re.fullmatch('a...', inst_str):
			i = (b1l << 8) + b2
		elif re.fullmatch('d...', inst_str):
			y = v[b2h]
			addr = i
			for _ in range(b2l):
				x = v[b1l]
				for xx in range(8):
					b = bin(mem[addr])[2:]
					b = '0' * (8 - len(b)) + b
					b = b[xx] == '1'
					screen_arr[y][x] = screen_arr[y][x] ^ b
					x += 1
				y += 1
				addr += 1
		elif re.fullmatch('e..1', inst_str):
			if v[b1l] != event:
				ip += inst_size
		elif re.fullmatch('7...', inst_str):
			n = v[b1l] + b2
			v[b1l] = n % 256
		elif re.fullmatch('f.07', inst_str):
			v[b1l] = delay
		elif re.fullmatch('3...', inst_str):
			if v[b1l] == b2:
				ip += inst_size
		elif re.fullmatch('f.15', inst_str):
			delay = v[b1l]
		elif re.fullmatch('1...', inst_str):
			ip = (b1l << 8) + b2
			ip -= inst_size
		elif re.fullmatch('', inst_str):
			return
		else:
			running = False

		size = 12
		screen.fill(Colors.black)
		for y in range(len(screen_arr)):
			for x in range(len(screen_arr[y])):
				if screen_arr[y][x]:
					pyg.draw.rect(screen, Colors.white, ((x*size,y*size), (size,size)), False)
		for y in range(len(screen_arr)+1):
			pyg.draw.line(screen, Colors.blue, (0,y*size), (800,y*size), 1)
			for x in range(len(screen_arr[0])+1):
				pyg.draw.line(screen, Colors.blue, (x*size,0), (x*size,600), 1)
		pyg.display.update()

		for e in pyg.fastevent.get():
			if e.type == pyg.QUIT:
				running = False
				break
			elif e.type == pyg.KEYDOWN:
				if e.key == pyg.K_w:
					event = 0x5
				elif e.key == pyg.K_a:
					event = 0x7
				elif e.key == pyg.K_s:
					event = 0x8
				elif e.key == pyg.K_d:
					event = 0x9
				else:
					event = 0x0
			else:
				event = 0x0
		delay = 0

		ip += inst_size
		print([hex(x) for x in v])
		print(hex(i))
		print(delay)
		print(hex(ip))
		print()
		# sleep(10/1000)

	pyg.quit()


if __name__ == "__main__":
	main()
