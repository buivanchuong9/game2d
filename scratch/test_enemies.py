
import pygame
import sys
import os

# Mock pygame to avoid window creation
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

# Add current dir to path
sys.path.append('.')

from enemy import *

enemies_to_test = [Goblin, EvilWizard, DashingGoblin, Skeleton, FlyingEye, Mushroom, BigFlyingEye, ZombieCrawler, ZombieExploder, ZombiePoison, ZombieCommander, OldGuardian, TeleportingMushroom]

print("Testing Enemy Initializations...")
for cls in enemies_to_test:
    try:
        e = cls(100, 100)
        print(f"[OK] {cls.__name__}")
    except TypeError as e:
        print(f"[FAIL] {cls.__name__}: {e}")
    except Exception as e:
        print(f"[ERROR] {cls.__name__}: {e}")

pygame.quit()
