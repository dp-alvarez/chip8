from dataclasses import dataclass
from .system import SystemConfig
from gui.colors import Colors


@dataclass
class WindowConfig:
	draw_interval: float = 1/60
	draw_size: int = 12
	margin: int = 10
	font_size: int = 24
	font: str = "Liberation Mono"
	screen_size: tuple[int,int] = (SystemConfig.screen_size[0]*draw_size+1, SystemConfig.screen_size[1]*draw_size+1)
	screen_pos: tuple[int,int] = (margin, margin)
	overlay_size: tuple[int,int] = (screen_size[0], 2*font_size)
	overlay_pos: tuple[int,int] = (screen_pos[0], 2*margin+screen_size[1])
	window_size: tuple[int,int] = (2*margin+max(screen_size[0],overlay_size[0]), 3*margin+screen_size[1]+overlay_size[1])
	draw_color: Colors = Colors.white
	grid_color: Colors = Colors.black
	window_bg: Colors = Colors.black
	caption: str = "CHIP8 Emu"
