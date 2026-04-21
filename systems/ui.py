# --- UI functions and helpers ---
import pygame
import os

# Absolute path of the game directory — used to resolve all asset paths
# without relying on the working directory (no os.chdir here).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_ui_font(size, bold=False):
	# Prefer fonts with broad Unicode coverage so Vietnamese accents render correctly.
	path_candidates = [
		"/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
		"/System/Library/Fonts/Supplemental/Arial.ttf",
		"/System/Library/Fonts/Supplemental/Verdana.ttf",
		"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
		"/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
		"C:/Windows/Fonts/arial.ttf",
		"C:/Windows/Fonts/tahoma.ttf",
	]
	for path in path_candidates:
		if os.path.exists(path):
			try:
				return pygame.font.Font(path, size)
			except Exception:
				pass

	name_candidates = ["arial unicode ms", "arial", "verdana", "tahoma", "dejavu sans", "noto sans"]
	for name in name_candidates:
		path = pygame.font.match_font(name, bold=bold)
		if path:
			try:
				return pygame.font.Font(path, size)
			except Exception:
				pass

	return pygame.font.Font(None, size)

def wrap_text(text, font, max_width):
	words = text.split()
	if not words:
		return [""]
	lines = []
	current = words[0]
	for word in words[1:]:
		trial = f"{current} {word}"
		if font.size(trial)[0] <= max_width:
			current = trial
		else:
			lines.append(current)
			current = word
	lines.append(current)
	return lines

def safe_load(path, size):
	"""Load and scale a sprite. Path is resolved relative to BASE_DIR."""
	try:
		abs_path = os.path.join(BASE_DIR, path) if not os.path.isabs(path) else path
		image = pygame.image.load(abs_path).convert_alpha()
		return pygame.transform.scale(image, size)
	except Exception:
		fallback = pygame.Surface(size, pygame.SRCALPHA)
		fallback.fill((100, 100, 100, 255))
		return fallback

def safe_sheet_frame(path, rect, size):
	"""Load a frame from a sprite sheet. Path is resolved relative to BASE_DIR."""
	try:
		abs_path = os.path.join(BASE_DIR, path) if not os.path.isabs(path) else path
		sheet = pygame.image.load(abs_path).convert_alpha()
		frame = sheet.subsurface(rect)
		return pygame.transform.scale(frame, size)
	except Exception:
		fallback = pygame.Surface(size, pygame.SRCALPHA)
		fallback.fill((120, 120, 120, 255))
		return fallback
# ui.py
# Module quản lý giao diện người dùng, font, panel, sidebar, overlay...
# Tách các hàm và class liên quan đến UI từ main.py

# Để trống, sẽ bổ sung sau khi tách xong các phần liên quan
