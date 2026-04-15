# --- UI functions and helpers ---
import pygame
import os

def load_ui_font(size, bold=False):
	path = pygame.font.match_font("Arial", bold=bold)
	if path:
		return pygame.font.Font(path, size)
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
	try:
		image = pygame.image.load(path).convert_alpha()
		return pygame.transform.scale(image, size)
	except Exception:
		fallback = pygame.Surface(size, pygame.SRCALPHA)
		fallback.fill((100, 100, 100, 255))
		return fallback

def safe_sheet_frame(path, rect, size):
	try:
		sheet = pygame.image.load(path).convert_alpha()
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
