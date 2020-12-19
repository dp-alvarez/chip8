from dataclasses import dataclass, InitVar, field
from .system import SystemConfig
from gui.colors import Colors


@dataclass
class WindowConfig:
	sysconfig: InitVar[SystemConfig] = None
	draw_interval: float = 1/60
	draw_size: int = 12
	margin: int = 10
	font_size: int = 24
	font: str = "Liberation Mono"
	screen_pos: tuple[int,int] = (margin, margin)
	screen_size: tuple[int,int] = field(init=False)
	overlay_size: tuple[int,int] = field(init=False)
	overlay_pos: tuple[int,int] = field(init=False)
	window_size: tuple[int,int] = field(init=False)
	draw_color: Colors = Colors.white
	grid_color: Colors = Colors.black
	window_bg: Colors = Colors.black
	caption: str = "CHIP8 Emu"

	def __post_init__(self, sysconfig):
		if not sysconfig:
			sysconfig = SystemConfig()
		self.screen_size = (sysconfig.screen_size[0]*self.draw_size+1, sysconfig.screen_size[1]*self.draw_size+1)
		self.overlay_size = (self.screen_size[0], 2*self.font_size)
		self.overlay_pos = (self.screen_pos[0], 2*self.margin+self.screen_size[1])
		self.window_size = (2*self.margin+max(self.screen_size[0],self.overlay_size[0]), 3*self.margin+self.screen_size[1]+self.overlay_size[1])
