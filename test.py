import os

os.environ["LASTROOF_WINDOWED"] = "1"

import math
import pygame

import core.game as cg


class DebugSandbox:
    def __init__(self):
        self.game = cg.Game()
        self.status = "Windowed debug sandbox ready."
        self.reset_chapter(self.game.chapter_index)

    def reset_chapter(self, index):
        self.game.set_chapter(index % len(self.game.chapters))
        self.game.state = "playing"
        self.game.story_enemies = []
        self.game.chapter.items = []
        self.game.chapter.npcs = []
        self.game.dialog_npc = None
        self.game.dialog_queue = []
        self.game.show_shop = False
        self.game.show_map = False
        self.game.enemies_remaining_to_spawn = 0
        self.game.popup = f"Debug chapter: {self.game.chapter.title}"
        self.game.popup_timer = pygame.time.get_ticks() + 1500

    def stabilize_game(self):
        self.game.dialog_npc = None
        self.game.dialog_queue = []
        self.game.show_shop = False
        self.game.enemies_remaining_to_spawn = 0

    def mouse_world_tile(self):
        mx, my = pygame.mouse.get_pos()
        wx, wy = self.game.camera.screen_to_world(mx, my)
        tx = max(1, min(cg.GRID_SIZE - 2, int(wx // cg.TILE_SIZE)))
        ty = max(1, min(cg.GRID_SIZE - 2, int(wy // cg.TILE_SIZE)))
        return tx, ty

    def _tile_occupied(self, tile):
        if tile in self.game.current_blocked:
            return True
        return any((not item.collected) and item.grid_pos == tile for item in self.game.chapter.items)

    def _find_free_tile(self, base_tile, radius=3):
        tx, ty = base_tile
        for r in range(0, max(0, radius) + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    tile = (tx + dx, ty + dy)
                    if not (1 <= tile[0] < cg.GRID_SIZE - 1 and 1 <= tile[1] < cg.GRID_SIZE - 1):
                        continue
                    if not self._tile_occupied(tile):
                        return tile
        return None

    def spawn_enemy(self, enemy_cls, archetype="basic"):
        tile = self._find_free_tile(self.mouse_world_tile(), radius=4)
        if tile is None:
            self.status = "No free tile for enemy spawn."
            return
        ex = tile[0] * cg.TILE_SIZE + cg.TILE_SIZE // 2
        ey = tile[1] * cg.TILE_SIZE + cg.TILE_SIZE // 2
        enemy = enemy_cls(ex, ey)
        enemy.obstacle_map = self.game.build_obstacle_grid()
        arch = "boss" if enemy_cls in {cg.BigFlyingEye, cg.OldGuardian} else archetype
        self.game.story_enemies.append(cg.StoryEnemy(enemy, arch, tile))
        self.status = f"Spawned {enemy_cls.__name__} at {tile}."

    def spawn_item(self, item_type, name, description, amount=0, color=cg.YELLOW, weapon_data=None):
        tile = self._find_free_tile(self.mouse_world_tile(), radius=4)
        if tile is None:
            self.status = "No free tile for item spawn."
            return
        item = cg.ItemPickup(tile, name, description, item_type, amount=amount, color=color, weapon_data=weapon_data)
        if item_type == "weapon_drop" and weapon_data:
            sprite = cg.ALL_GRAPHICS_SURFACES.get(weapon_data["image_path"])
            if sprite:
                item.sprite_surface = pygame.transform.scale(sprite, (32, 24))
        self.game.chapter.items.append(item)
        self.status = f"Spawned {item_type} at {tile}."

    def spawn_money(self, amount=1):
        tile = self.mouse_world_tile()
        if self.game.spawn_money_drop_near(tile, amount=amount, radius=4):
            self.status = f"Spawned money near {tile}."
        else:
            self.status = "Failed to spawn money."

    def kill_nearest_enemy(self):
        alive = [entry for entry in self.game.story_enemies if not entry.enemy.is_dead]
        if not alive:
            self.status = "No alive enemy to kill."
            return
        nearest = min(alive, key=lambda entry: math.hypot(entry.enemy.x - self.game.player.x, entry.enemy.y - self.game.player.y))
        nearest.enemy.take_damage(999999)
        self.status = f"Killed {nearest.enemy.__class__.__name__}."

    def teleport_player(self):
        tile = self._find_free_tile(self.mouse_world_tile(), radius=4)
        if tile is None:
            self.status = "No free tile to teleport."
            return
        self.game.player.x = tile[0] * cg.TILE_SIZE + cg.TILE_SIZE // 2
        self.game.player.y = tile[1] * cg.TILE_SIZE + cg.TILE_SIZE // 2
        self.status = f"Teleported player to {tile}."

    def clear_runtime_objects(self):
        self.game.story_enemies = []
        self.game.chapter.items = []
        self.status = "Cleared enemies and items."

    def handle_debug_key(self, event):
        if event.key == pygame.K_1:
            self.spawn_enemy(cg.Goblin, "basic")
        elif event.key == pygame.K_2:
            self.spawn_enemy(cg.Skeleton, "special")
        elif event.key == pygame.K_3:
            self.spawn_enemy(cg.Mushroom, "tank")
        elif event.key == pygame.K_4:
            self.spawn_enemy(cg.FlyingEye, "fast")
        elif event.key == pygame.K_5:
            self.spawn_enemy(cg.EvilWizard, "ranged")
        elif event.key == pygame.K_6:
            self.spawn_enemy(cg.OldGuardian, "boss")
        elif event.key == pygame.K_7:
            self.spawn_money(amount=1)
        elif event.key == pygame.K_8:
            self.spawn_item("heal", "Debug Medkit", "Restores health.", amount=50, color=cg.GREEN)
        elif event.key == pygame.K_9:
            self.spawn_item("ammo", "Debug Ammo", "Adds reserve ammo.", amount=30, color=cg.WHITE)
        elif event.key == pygame.K_0:
            self.spawn_item("armor", "Debug Armor", "Adds armor.", amount=25, color=cg.CYAN)
        elif event.key == pygame.K_MINUS:
            weapon_data = dict(cg.WEAPON_DROP_POOL[0])
            self.spawn_item("weapon_drop", weapon_data["name"], "Debug weapon drop.", color=cg.ORANGE, weapon_data=weapon_data)
        elif event.key == pygame.K_k:
            self.kill_nearest_enemy()
        elif event.key == pygame.K_t:
            self.teleport_player()
        elif event.key == pygame.K_c:
            self.game.dialog_npc = None
            self.game.dialog_queue = []
            self.status = "Cleared dialogue queue."
        elif event.key == pygame.K_x:
            self.clear_runtime_objects()
        elif event.key == pygame.K_LEFTBRACKET:
            self.reset_chapter(self.game.chapter_index - 1)
        elif event.key == pygame.K_RIGHTBRACKET:
            self.reset_chapter(self.game.chapter_index + 1)

    def draw_overlay(self):
        money_items = [item for item in self.game.chapter.items if (not item.collected) and item.item_type == "money"]
        alive = [entry for entry in self.game.story_enemies if not entry.enemy.is_dead]
        mouse_tile = self.mouse_world_tile()

        panel = pygame.Surface((460, 180), pygame.SRCALPHA)
        panel.fill((10, 12, 18, 190))
        cg.screen.blit(panel, (14, cg.SCREEN_HEIGHT - 194))

        lines = [
            f"[ / ] chapter | T teleport | K kill nearest | X clear runtime",
            f"1 Goblin 2 Skeleton 3 Mushroom 4 Eye 5 Wizard 6 Guardian",
            f"7 money 8 medkit 9 ammo 0 armor - weapon drop | C clear dialog",
            f"mouse tile={mouse_tile} player_money={self.game.money} money_on_ground={len(money_items)} alive_enemies={len(alive)}",
            self.status,
        ]

        yy = cg.SCREEN_HEIGHT - 186
        for line in lines:
            label = self.game.font_small.render(line, True, cg.WHITE)
            cg.screen.blit(label, (24, yy))
            yy += 28

        pygame.display.flip()


def main():
    sandbox = DebugSandbox()

    while True:
        for event in pygame.event.get():
            sandbox.game.handle_event(event)
            if sandbox.game.state == "playing" and event.type == pygame.KEYDOWN:
                sandbox.handle_debug_key(event)

        sandbox.stabilize_game()
        sandbox.game.update()
        sandbox.game.draw()
        sandbox.draw_overlay()
        cg.clock.tick(cg.FPS)


if __name__ == "__main__":
    main()
