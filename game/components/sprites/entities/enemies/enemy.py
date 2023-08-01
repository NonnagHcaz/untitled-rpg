import random
import pygame

from game.components.sprites.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, mingle_chance=0.2, detection_distance=300, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mingle_chance = mingle_chance
        self.mingle_timer = 0
        self.detection_distance = detection_distance
        self.attack_range = 0

    def update(self, *args, camera=None, player=None, **kwargs):
        super().update(*args, **kwargs)
        if player and camera:
            distance_to_player = self.get_distance_to_player(player, camera)
            if distance_to_player <= self.detection_distance:
                self.follow_and_attack_player(player, camera)
            else:
                self.wander_around()

    def wander_around(self):
        if not self.mingle_timer:
            self.mingle_timer = 30
            if random.random() < self.mingle_chance:
                move_x = random.choice([-1, 0, 1])
                move_y = random.choice([-1, 0, 1])
                # TODO: Validate movement
                if move_x == -1:
                    self.direction = self.Direction.WEST

                else:
                    self.direction = self.Direction.EAST

                move_vector = pygame.Vector2(
                    move_x * self.walk_speed, move_y * self.walk_speed
                )
                self.rect.move_ip(move_vector)
        else:
            self.mingle_timer = max(0, self.mingle_timer - 1)

    def follow_and_attack_player(self, player, camera):
        # Calculate the direction vector towards the player
        player_world_pos = player.rect.topleft + camera
        enemy_world_pos = self.rect.topleft + camera

        dx = player_world_pos[0] - enemy_world_pos[0]
        dy = player_world_pos[1] - enemy_world_pos[1]
        distance = (dx**2 + dy**2) ** 0.5

        if distance > 0:
            direction_vector = pygame.Vector2(dx / distance, dy / distance)
        else:
            direction_vector = pygame.Vector2(0, 0)

        # Move towards the player
        move_vector = direction_vector * self.walk_speed
        move_vector = camera.apply_inverse_zoom(move_vector)
        self.rect.move_ip(move_vector)

        # Flip the enemy sprite to face the player
        if direction_vector.x > 0:
            self.flip(True, False)  # Flip horizontally (face right)
        else:
            self.flip(False, False)  # Unflip (face left)

        # Attack the player if within attack range
        if distance <= self.attack_range:
            self.attack(player)

    def get_distance_to_player(self, player, camera):
        # Convert screen coordinates of player and enemy to world coordinates
        player_world_pos = player.rect.topleft + camera
        enemy_world_pos = self.rect.topleft + camera

        # Calculate distance between player and enemy in world coordinates
        dx = player_world_pos[0] - enemy_world_pos[0]
        dy = player_world_pos[1] - enemy_world_pos[1]
        distance = (dx**2 + dy**2) ** 0.5

        return distance
