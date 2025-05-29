#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random
import math
from constants import *


def create_enemy(x, y, enemy_type, scale):
    scale *= 2
    if enemy_type == EnemyType.LOGGER.value:
        return LumberJack(x, y, scale)
    elif enemy_type == EnemyType.POLLUTER.value:
        return Polluter(x, y, scale)
    elif enemy_type == EnemyType.MACHINE.value:
        return LoggingMachine(x, y, scale//2*3)
    elif enemy_type == EnemyType.FLAMETHROWER.value:
        return FireThrower(x, y, scale)
    elif enemy_type == EnemyType.BOSS.value:
        return GreedyMerchant(x, y, scale)
    else:
        return Enemy(x, y, enemy_type, scale)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, scale):
        pygame.sprite.Sprite.__init__(self)
        self.enemy_type = enemy_type
        self.scale = scale
        self.direction = random.choice([-1, 1])  # 随机初始方向
        self.flip = self.direction == -1
        self.move_counter = 0
        self.idle_counter = 0
        self.moving = True

        # 根据敌人类型加载图像
        self.image = self.load_image(f"enemy_{enemy_type}", scale)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # 属性设置
        self.speed = random.uniform(5, 10)
        self.health = 50
        self.max_health = 50
        self.strength = 10
        self.alive = True
        self.hit = False
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.velocity_y = 0
        # 减速效果变量
        self.original_speed = None  # 存储原始速度
        self.slow_duration = 0      # 减速持续时间
        self.shield_active = False

    def load_image(self, name, scale=1):

        # 像素大小
        pixel_size = 4

        def draw_pixel(surface, x, y, color):
            pygame.draw.rect(surface, color, (x * pixel_size, y * pixel_size, pixel_size, pixel_size))

        black = (1, 1, 1)
        if "enemy_0" in name.lower():  # Logger - 伐木工
            # 创建2位像素风格的角色图像
            img = pygame.Surface((12*pixel_size, 8*pixel_size))  # 增大基础尺寸以匹配像素艺术
            img.fill((0, 0, 0, 0))  # 透明背景
            img.set_colorkey((0, 0, 0))  # 设置黑色为透明
            # 颜色定义
            skin = (255, 219, 172)
            hair = (101, 67, 33)
            shirt = (139, 69, 19)
            pants = (65, 105, 225)
            axe = (192, 192, 192)
            axe_handle = (139, 69, 19)

            # 头发
            for x in range(6, 10):
                draw_pixel(img, x, 1, hair)

            # 头部
            for x in range(6, 10):
                for y in range(2, 4):
                    draw_pixel(img, x, y, skin)

            # 眼睛
            draw_pixel(img, 6, 3, black)
            draw_pixel(img, 8, 3, black)

            # 身体
            for x in range(6, 10):
                for y in range(4, 6):
                    draw_pixel(img, x, y, shirt)

            # 手臂
            draw_pixel(img, 5, 4, skin)
            draw_pixel(img, 10, 4, skin)
            draw_pixel(img, 4, 5, skin)
            draw_pixel(img, 11, 5, skin)

            # 腿部
            for x in range(6, 10):
                for y in range(6, 8):
                    draw_pixel(img, x, y, pants)

            # 斧头柄
            for y in range(3, 6):
                draw_pixel(img, 3, y, axe_handle)

            # 斧头刃
            draw_pixel(img, 2, 2, axe)
            draw_pixel(img, 2, 3, axe)
            draw_pixel(img, 1, 3, axe)

        elif "enemy_1" in name.lower():  # Polluter - 污染者
            # 创建2位像素风格的角色图像
            img = pygame.Surface((14*pixel_size, 7*pixel_size))  # 增大基础尺寸以匹配像素艺术
            img.fill((0, 0, 0, 0))  # 透明背景
            img.set_colorkey((0, 0, 0))  # 设置黑色为透明
            # 颜色定义
            hazmat = (255, 255, 0)
            mask = (255, 0, 0)
            tank = (102, 102, 102)
            tube = (0, 255, 0)

            # 防毒面具
            for x in range(6, 10):
                draw_pixel(img, x, 1, mask)

            # 防化服身体
            for x in range(6, 10):
                for y in range(2, 5):
                    draw_pixel(img, x, y, hazmat)

            # 面具细节
            draw_pixel(img, 7, 2, black)
            draw_pixel(img, 8, 2, black)

            # 手臂
            draw_pixel(img, 5, 3, hazmat)
            draw_pixel(img, 10, 3, hazmat)
            draw_pixel(img, 4, 4, hazmat)
            draw_pixel(img, 11, 4, hazmat)

            # 腿部
            for x in range(6, 10):
                for y in range(5, 7):
                    draw_pixel(img, x, y, hazmat)

            # 毒性罐
            for x in range(11, 13):
                for y in range(2, 4):
                    draw_pixel(img, x, y, tank)

            # 毒性管道
            draw_pixel(img, 3, 4, tube)
            draw_pixel(img, 2, 5, tube)
            draw_pixel(img, 1, 6, tube)

        elif "enemy_2" in name.lower():  # Logging Machine - 伐木机
            # 创建2位像素风格的角色图像
            img = pygame.Surface((14*pixel_size, 6*pixel_size))  # 增大基础尺寸以匹配像素艺术
            img.fill((0, 0, 0, 0))  # 透明背景
            img.set_colorkey((0, 0, 0))  # 设置黑色为透明
            # 颜色定义
            orange = (255, 140, 0)
            metal = (128, 128, 128)
            dark_metal = (64, 64, 64)
            # black = (1, 1, 1)

            # 主体
            for x in range(4, 12):
                for y in range(2, 5):
                    draw_pixel(img, x, y, orange)

            # 窗户/驾驶室
            draw_pixel(img, 5, 3, black)
            draw_pixel(img, 6, 3, black)
            draw_pixel(img, 9, 3, black)
            draw_pixel(img, 10, 3, black)

            # 切割臂
            for x in range(2, 4):
                for y in range(3, 5):
                    draw_pixel(img, x, y, metal)

            # 锯片
            draw_pixel(img, 1, 2, metal)
            draw_pixel(img, 0, 3, metal)
            draw_pixel(img, 1, 4, metal)
            draw_pixel(img, 0, 5, metal)

            # 履带
            for x in range(4, 12):
                draw_pixel(img, x, 5, black)

            # 排气管
            draw_pixel(img, 12, 1, dark_metal)
            draw_pixel(img, 13, 0, (102, 102, 102))

        elif "enemy_3" in name.lower():  # Fire Thrower - 火焰喷射器
            # 创建2位像素风格的角色图像
            img = pygame.Surface((13*pixel_size, 7*pixel_size))  # 增大基础尺寸以匹配像素艺术
            img.fill((0, 0, 0, 0))  # 透明背景
            img.set_colorkey((0, 0, 0))  # 设置黑色为透明
            # 颜色定义
            skin = (255, 219, 172)
            gear = (101, 67, 33)
            tank = (255, 0, 0)
            flame = (255, 69, 0)
            orange = (255, 140, 0)
            yellow = (255, 255, 0)

            # 头盔
            for x in range(6, 10):
                draw_pixel(img, x, 1, gear)

            # 头部
            for x in range(6, 10):
                draw_pixel(img, x, 2, skin)

            # 眼睛
            draw_pixel(img, 6, 2, black)
            draw_pixel(img, 8, 2, black)

            # 身体
            for x in range(6, 10):
                for y in range(3, 5):
                    draw_pixel(img, x, y, gear)

            # 手臂
            draw_pixel(img, 5, 3, skin)
            draw_pixel(img, 10, 3, skin)
            draw_pixel(img, 4, 4, skin)
            draw_pixel(img, 11, 4, skin)

            # 腿部
            for x in range(6, 10):
                for y in range(5, 7):
                    draw_pixel(img, x, y, gear)

            # 燃料罐
            for x in range(11, 13):
                for y in range(2, 4):
                    draw_pixel(img, x, y, tank)

            # 火焰喷射器喷嘴
            draw_pixel(img, 3, 4, (128, 128, 128))
            draw_pixel(img, 2, 4, (128, 128, 128))

            # 火焰
            draw_pixel(img, 1, 4, flame)
            draw_pixel(img, 0, 4, orange)
            draw_pixel(img, 1, 3, orange)
            draw_pixel(img, 0, 3, yellow)
            draw_pixel(img, 1, 5, orange)
            draw_pixel(img, 0, 5, yellow)

        elif "enemy_4" in name.lower():  # Boss - Greedy Merchant - 贪婪商人
            img = pygame.Surface((12*pixel_size, 8*pixel_size))  # 增大基础尺寸以匹配像素艺术
            img.fill((0, 0, 0, 0))  # 透明背景
            img.set_colorkey((0, 0, 0))  # 设置黑色为透明
            # 颜色定义
            skin = (255, 219, 172)
            suit = (0, 0, 128)
            gold = (255, 215, 0)
            red = (220, 20, 60)
            purple = (128, 0, 128)
            green = (0, 255, 0)
            # black = (0, 0, 0)

            # 礼帽
            for x in range(6, 10):
                draw_pixel(img, x, 0, black)
            for x in range(5, 11):
                draw_pixel(img, x, 1, black)

            # 头部
            for x in range(6, 10):
                draw_pixel(img, x, 2, skin)

            # 胡子和邪恶笑容
            for x in range(6, 10):
                draw_pixel(img, x, 3, black)

            # 邪恶的眼睛
            draw_pixel(img, 6, 2, red)
            draw_pixel(img, 8, 2, red)

            # 正装
            for x in range(6, 10):
                draw_pixel(img, x, 4, suit)
            for x in range(6, 10):
                draw_pixel(img, x, 5, suit)

            # 领结
            draw_pixel(img, 7, 4, red)
            draw_pixel(img, 8, 4, red)

            # 手臂
            draw_pixel(img, 5, 4, skin)
            draw_pixel(img, 10, 4, skin)
            draw_pixel(img, 4, 5, suit)
            draw_pixel(img, 11, 5, suit)

            # 钱袋
            draw_pixel(img, 3, 4, gold)
            draw_pixel(img, 2, 5, gold)
            draw_pixel(img, 3, 5, gold)
            draw_pixel(img, 2, 6, gold)

            # 美元符号
            draw_pixel(img, 2, 5, green)

            # 腿部
            for x in range(6, 10):
                draw_pixel(img, x, 6, suit)

            # 鞋子
            for x in range(6, 10):
                draw_pixel(img, x, 7, black)

            # 魔法光环（Boss效果）
            draw_pixel(img, 5, 2, purple)
            draw_pixel(img, 10, 2, purple)
            draw_pixel(img, 4, 4, purple)
            draw_pixel(img, 11, 4, purple)
            draw_pixel(img, 5, 6, purple)
            draw_pixel(img, 10, 6, purple)

        else:
            # 创建2位像素风格的角色图像
            img = pygame.Surface((40, 30))  # 增大基础尺寸以匹配像素艺术
            img.fill((0, 0, 0, 0))  # 透明背景
            img.set_colorkey((0, 0, 0))  # 设置黑色为透明
            img.fill((200, 0, 0))  # 其他敌人用红色表示
        # 缩放图片
        width = img.get_width()
        height = img.get_height()
        img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
        img = pygame.transform.flip(img, True, False)
        return img

    # def load_image(self, name, scale=1):
    #     # 占位实现，实际游戏中应加载真实图片
    #     img = pygame.Surface((50, 80))
    #
    #     if "enemy_0" in name.lower():
    #         img.fill((139, 69, 19))  # 棕色表示伐木工
    #     elif "enemy_1" in name.lower():
    #         img.fill((128, 0, 128))  # 紫色表示污染者
    #     elif "enemy_2" in name.lower():
    #         img.fill((169, 169, 169))  # 灰色表示机械敌人
    #     elif "enemy_3" in name.lower():
    #         img.fill((255, 69, 0))  # 橙红色表示火焰敌人
    #     else:
    #         img.fill((200, 0, 0))  # 其他敌人用红色表示
    #
    #     # 缩放图片
    #     width = img.get_width()
    #     height = img.get_height()
    #     img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
    #
    #     return img

    def update(self, world, player, particles):
        dx = 0
        dy = 0

        if self.alive:
            # AI行为
            if self.moving:
                dx = self.direction * self.speed
                self.move_counter += 1

                # 检测边缘或障碍物，转向
                if self.move_counter > random.randint(100, 200) or world.tile_collide(self.rect.x + dx, self.rect.y,
                                                                                      self.rect.width,
                                                                                      self.rect.height):
                    self.direction *= -1
                    self.flip = not self.flip
                    self.move_counter = 0
                    self.idle_counter = random.randint(5, 20)  # 设置闲置时间
                    self.moving = False
            else:
                self.idle_counter -= 1
                if self.idle_counter <= 0:
                    self.moving = True

            # 寻找玩家
            player_dist = math.sqrt((player.rect.centerx - self.rect.centerx) ** 2 +
                                    (player.rect.centery - self.rect.centery) ** 2)
            if player_dist < 500 and random.random() < 0.90:  # 60%几率追逐玩家
                if player.rect.centerx < self.rect.centerx:
                    self.direction = -1
                    self.flip = True
                else:
                    self.direction = 1
                    self.flip = False

            # 应用重力
            self.velocity_y += GRAVITY
            dy += self.velocity_y

            # 检查与世界的碰撞
            for tile in world.tile_list:
                # 水平碰撞
                # if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                #     dx = 0
                #     self.direction *= -1  # 改变方向
                #     self.flip = not self.flip

                # 垂直碰撞
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                    if self.velocity_y < 0:  # 跳跃时碰到天花板
                        dy = tile[1].bottom - self.rect.top
                        self.velocity_y = 0
                    elif self.velocity_y >= 0:  # 下落时碰到地面
                        dy = tile[1].top - self.rect.bottom
                        self.velocity_y = 0

            # 更新位置
            self.rect.x += dx
            self.rect.y += dy

            # 检查是否掉出世界边界
            if self.rect.y > world.world_height or self.rect.y < -500:
                # 敌人掉出世界，重置到适当位置
                self.reset_to_spawn_point(world, player)

            # 攻击玩家
            if player_dist < 50 and self.attack_cooldown == 0 and not player.is_invincible():
                player.health -= self.strength
                player.hit = True
                player.hit_cooldown = 10
                self.attack_cooldown = 60  # 1秒冷却
                particles.add_particles(player.rect.centerx, player.rect.centery, RED, count=15)

            # 更新冷却时间
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1

            if self.hit_cooldown > 0:
                self.hit_cooldown -= 1

            # 检查生命值
            if self.health <= 0:
                self.alive = False
                particles.add_particles(self.rect.centerx, self.rect.centery, RED, count=40, size=8)

            # 处理减速效果计时
            if self.slow_duration > 0:
                self.slow_duration -= 1
                # 如果减速时间结束，恢复原始速度
                if self.slow_duration == 0 and self.original_speed is not None:
                    self.speed = self.original_speed
                    self.original_speed = None

    # 添加重置到初始位置的方法
    def reset_to_spawn_point(self, world, player):
        # 记录敌人类型，以便正确重置
        enemy_type = self.enemy_type

        # 根据不同类型敌人可能有不同的重生策略
        if hasattr(world, 'enemy_spawn_points') and world.enemy_spawn_points:
            # 如果世界有预定义的敌人生成点，随机选择一个
            spawn_point = random.choice(world.enemy_spawn_points)
            self.rect.x = spawn_point[0]
            self.rect.y = spawn_point[1]
        else:
            # 如果没有预定义点，则在离玩家一定距离的位置生成
            # 确保敌人不会直接生成在玩家附近
            min_dist = 300  # 与玩家的最小距离

            # 尝试找到合适的生成位置
            for _ in range(10):  # 最多尝试10次
                # 在可见区域附近随机选择一个点
                spawn_x = random.randint(max(0, player.rect.x - 800), player.rect.x + 800)
                spawn_y = random.randint(max(0, player.rect.y - 400), player.rect.y + 400)

                # 计算与玩家的距离
                dist = math.sqrt((spawn_x - player.rect.x) ** 2 + (spawn_y - player.rect.y) ** 2)

                # 如果距离足够远且位置有效，则使用该点
                if dist > min_dist and not world.is_position_solid(spawn_x, spawn_y):
                    self.rect.x = spawn_x
                    self.rect.y = spawn_y
                    break
            else:
                # 如果找不到合适的位置，使用默认位置
                self.rect.x = player.rect.x + 500 * random.choice([-1, 1])
                self.rect.y = player.rect.y - 100


    def draw(self, surface, scroll):
        if self.alive:
            # 绘制敌人
            surface.blit(pygame.transform.flip(self.image, self.flip, False),
                         (self.rect.x - scroll[0], self.rect.y - scroll[1]))

            # 绘制生命条
            pygame.draw.rect(surface, RED, (self.rect.x - scroll[0], self.rect.y - 15 - scroll[1], self.rect.width, 5))
            if self.health > 0:
                pygame.draw.rect(surface, GREEN,
                                (self.rect.x - scroll[0], self.rect.y - 15 - scroll[1],
                                 int(self.rect.width * (self.health/self.max_health)), 5))

            # 闪烁效果（受伤时）
            if self.hit_cooldown > 0:
                alpha = self.hit_cooldown * 25
                hit_surface = pygame.Surface((self.rect.width, self.rect.height))
                hit_surface.fill((255, 0, 0))
                hit_surface.set_alpha(alpha)
                surface.blit(hit_surface, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
    # 新增方法：应用减速效果

    def apply_slow(self, slow_factor, duration):
        # 如果尚未被减速或减速效果已经结束
        if self.original_speed is None:
            self.original_speed = self.speed
            self.speed *= slow_factor
            self.slow_duration = duration
        # 如果已经处于减速状态，只更新持续时间（不叠加减速效果）
        else:
            self.slow_duration = max(self.slow_duration, duration)


class LumberJack(Enemy):
    """伐木工敌人类型"""
    def __init__(self, x, y, scale=1):
        super().__init__(x, y, EnemyType.LOGGER.value, scale)
        self.health = 40
        self.max_health = 40
        self.strength = 8
        self.speed = random.uniform(4.5, 7.5)

class Polluter(Enemy):
    """污染者敌人类型"""
    def __init__(self, x, y, scale=1):
        super().__init__(x, y, EnemyType.POLLUTER.value, scale)
        self.health = 30
        self.max_health = 30
        self.strength = 5
        self.speed = random.uniform(3, 6)
        self.pollution_timer = 0
        self.pollution_interval = 120  # 每2秒释放污染
        self.pollution_range = 100

    def update(self, world, player, particles):
        super().update(world, player, particles)

        if self.alive:
            # 污染攻击逻辑
            self.pollution_timer += 1
            if self.pollution_timer >= self.pollution_interval:
                self.pollution_timer = 0
                # 范围伤害检测
                player_dist = math.sqrt((player.rect.centerx - self.rect.centerx)**2 +
                                      (player.rect.centery - self.rect.centery)**2)
                if player_dist <= self.pollution_range and not player.is_invincible():
                    player.health -= 3
                    player.hit = True
                    player.hit_cooldown = 5

                    # 影响森林健康度
                    world.forest_health -= 1
                    if world.forest_health < 0:
                        world.forest_health = 0

                    particles.add_particles(self.rect.centerx, self.rect.centery, PURPLE, count=30, speed=1, life=60)

class LoggingMachine(Enemy):
    """机械伐木机敌人类型"""
    def __init__(self, x, y, scale=1.5):
        super().__init__(x, y, EnemyType.MACHINE.value, scale)
        self.health = 100
        self.max_health = 100
        self.strength = 15
        self.speed = random.uniform(2.1, 3.6)
        self.attack_range = 80

    def update(self, world, player, particles):
        super().update(world, player, particles)

        if self.alive:
            # 扩大攻击范围
            player_dist = math.sqrt((player.rect.centerx - self.rect.centerx)**2 +
                                  (player.rect.centery - self.rect.centery)**2)
            if player_dist < self.attack_range and self.attack_cooldown == 0 and not player.is_invincible():
                player.health -= self.strength
                player.hit = True
                player.hit_cooldown = 15
                self.attack_cooldown = 90  # 1.5秒冷却
                particles.add_particles(player.rect.centerx, player.rect.centery, RED, count=25, size=6)

                # 对森林造成额外伤害
                world.forest_health -= 2
                if world.forest_health < 0:
                    world.forest_health = 0

class FireThrower(Enemy):
    """火焰喷射器敌人类型"""
    def __init__(self, x, y, scale=1):
        super().__init__(x, y, EnemyType.FLAMETHROWER.value, scale)
        self.health = 35
        self.max_health = 35
        self.strength = 7
        self.speed = random.uniform(3.6, 5.4)
        self.fire_range = 150
        self.fire_timer = 0
        self.burn_effect = []  # 存储被点燃的区域

    def update(self, world, player, particles):
        super().update(world, player, particles)

        if self.alive:
            # 远程火焰攻击
            self.fire_timer += 1
            if self.fire_timer >= 180:  # 3秒一次火焰攻击
                self.fire_timer = 0
                # 朝玩家方向喷火
                fire_direction = 1 if player.rect.centerx > self.rect.centerx else -1
                fire_x = self.rect.centerx + (fire_direction * 30)

                # 创建火焰效果
                for i in range(5):
                    fire_pos = (fire_x + (fire_direction * i * 20), self.rect.centery)
                    particles.add_particles(fire_pos[0], fire_pos[1], (255, 140, 0), count=15, life=90)
                    self.burn_effect.append((fire_pos, 120))  # 位置和持续时间

                # 检测玩家是否在火焰范围内
                player_in_range = (fire_direction == 1 and player.rect.centerx > self.rect.centerx and
                                 player.rect.centerx < self.rect.centerx + self.fire_range) or \
                                (fire_direction == -1 and player.rect.centerx < self.rect.centerx and
                                 player.rect.centerx > self.rect.centerx - self.fire_range)

                if player_in_range and abs(player.rect.centery - self.rect.centery) < 50 and not player.is_invincible():
                    player.health -= 12
                    player.hit = True
                    player.hit_cooldown = 10

                    # 持续燃烧效果
                    world.forest_health -= 3
                    if world.forest_health < 0:
                        world.forest_health = 0

            # 更新燃烧效果
            new_burn_effect = []
            for pos, time in self.burn_effect:
                time -= 1
                if time > 0:
                    new_burn_effect.append((pos, time))
                    if random.random() < 0.1:  # 10%几率产生火焰粒子
                        particles.add_particles(pos[0], pos[1], (255, 140, 0), count=3, life=30)

                    # 检测玩家是否在燃烧区域
                    if abs(player.rect.centerx - pos[0]) < 20 and abs(player.rect.centery - pos[1]) < 40 and not player.is_invincible():
                        player.health -= 0.5
                        if random.random() < 0.05:  # 低几率触发受伤效果
                            player.hit = True
                            player.hit_cooldown = 3

            self.burn_effect = new_burn_effect


class GreedyMerchant(Enemy):
    """贪婪商人BOSS类型，游戏最终BOSS"""

    def __init__(self, x, y, scale=2.0):
        super().__init__(x, y, EnemyType.BOSS.value, scale)
        self.health = 300
        self.max_health = 300
        self.strength = 25
        self.speed = random.uniform(3.0, 4.5)
        self.attack_range = 100
        self.attack_type = 0  # 0: 普通, 1: 污染, 2: 火焰, 3: 机械
        self.phase = 1  # BOSS战斗阶段
        self.phase_threshold = 0.7  # 进入第二阶段的生命值百分比
        self.minion_spawn_timer = 0
        self.minion_spawn_interval = 600  # 每10秒尝试召唤一次小怪
        self.special_attack_timer = 0
        self.special_attack_interval = 300  # 每5秒进行一次特殊攻击
        self.is_preparing_special = False
        self.preparation_time = 0

        # 方向控制优化
        self.direction_change_timer = 0
        self.target_direction_time = random.randint(120, 180)

        # 弹跳攻击相关
        self.is_jumping = False
        self.jump_height = -16
        self.jump_cooldown = 0

        # 护盾系统
        self.shield_active = False
        self.shield_health = 50
        self.shield_max_health = 50
        self.shield_cooldown = 0
        self.should_spawn_minions = False

    def update(self, world, player, particles):
        # 如果进入了下一阶段
        if self.phase == 1 and self.health <= self.max_health * self.phase_threshold:
            self.enter_phase_two(particles)

        # 召唤小怪逻辑
        self.minion_spawn_timer += 1
        if self.minion_spawn_timer >= self.minion_spawn_interval:
            self.minion_spawn_timer = 0
            if random.random() < 0.7:  # 70%几率召唤小怪
                self.spawn_minions(particles)

        # 特殊攻击逻辑
        if not self.is_preparing_special:
            self.special_attack_timer += 1
            if self.special_attack_timer >= self.special_attack_interval:
                self.special_attack_timer = 0
                self.prepare_special_attack()
        else:
            self.preparation_time -= 1
            if self.preparation_time <= 0:
                self.execute_special_attack(world, player, particles)
                self.is_preparing_special = False

        # 处理护盾冷却
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

        if not self.shield_active and self.shield_cooldown <= 0 and self.health < self.max_health * 0.5:
            # 在生命值低于50%时有机会激活护盾
            if random.random() < 0.01:  # 每帧1%的几率激活
                self.activate_shield(particles)

        # BOSS特殊移动模式
        self.boss_movement_pattern()

        # 调用基类的更新方法处理基本逻辑
        super().update(world, player, particles)

    def boss_movement_pattern(self):
        # 更加智能的方向控制
        self.direction_change_timer += 1
        if self.direction_change_timer >= self.target_direction_time:
            self.direction_change_timer = 0
            self.target_direction_time = random.randint(120, 180)

            # 在第二阶段增加跳跃几率
            if self.phase >= 2 and self.jump_cooldown <= 0 and random.random() < 0.4:
                self.velocity_y = self.jump_height
                self.is_jumping = True
                self.jump_cooldown = 90  # 1.5秒冷却
            else:
                self.direction *= -1
                self.flip = not self.flip

        # 处理跳跃冷却
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

    def prepare_special_attack(self):
        self.is_preparing_special = True
        self.preparation_time = 60  # 1秒准备时间
        self.attack_type = random.randint(0, 3)  # 随机选择攻击类型

    def execute_special_attack(self, world, player, particles):
        # 根据攻击类型执行不同的特殊攻击
        if self.attack_type == 0:  # 普通冲击波
            self.shockwave_attack(player, particles)
        elif self.attack_type == 1:  # 污染攻击
            self.pollution_attack(world, player, particles)
        elif self.attack_type == 2:  # 火焰攻击
            self.flame_attack(player, particles)
        elif self.attack_type == 3:  # 机械攻击
            self.machine_attack(world, player, particles)

    def shockwave_attack(self, player, particles):
        # 向两侧释放冲击波
        power = 18
        range_limit = 200

        # 计算与玩家的距离
        player_dist = math.sqrt((player.rect.centerx - self.rect.centerx) ** 2 +
                                (player.rect.centery - self.rect.centery) ** 2)

        # 如果玩家在范围内，造成伤害并击退
        if player_dist <= range_limit and not player.is_invincible():
            # 计算击退方向
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            # 标准化方向向量
            length = max(1, math.sqrt(dx * dx + dy * dy))
            dx /= length
            dy /= length

            # 施加击退力
            player.velocity_x = dx * power
            player.velocity_y = dy * power * 0.5 - 3  # 稍微向上的力

            # 造成伤害
            player.health -= self.strength * 0.7
            player.hit = True
            player.hit_cooldown = 15

        # 创建冲击波视觉效果
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x_offset = math.cos(rad) * 20
            y_offset = math.sin(rad) * 20
            particles.add_particles(self.rect.centerx + x_offset, self.rect.centery + y_offset,
                                    YELLOW, count=3, speed=3, life=40, size=5)

    def pollution_attack(self, world, player, particles):
        # 范围污染攻击，类似污染者但更强大
        pollution_range = 180

        # 计算与玩家的距离
        player_dist = math.sqrt((player.rect.centerx - self.rect.centerx) ** 2 +
                                (player.rect.centery - self.rect.centery) ** 2)

        # 如果玩家在范围内受到伤害
        if player_dist <= pollution_range and not player.is_invincible():
            player.health -= self.strength * 0.5
            player.hit = True
            player.hit_cooldown = 10

            # 影响森林健康度
            world.forest_health -= 3
            if world.forest_health < 0:
                world.forest_health = 0

        # 创建持续的污染云效果
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(30, pollution_range)
            x_offset = math.cos(angle) * distance
            y_offset = math.sin(angle) * distance
            particles.add_particles(self.rect.centerx + x_offset, self.rect.centery + y_offset,
                                    PURPLE, count=2, speed=0.5, life=120, size=4)

    def flame_attack(self, player, particles):
        # 多方向火焰喷射攻击
        flame_range = 220
        flame_damage = self.strength * 0.6

        # 喷射火焰的方向数
        flame_directions = 3 if self.phase == 1 else 5

        # 确定第一个方向是朝向玩家的
        base_angle = math.atan2(player.rect.centery - self.rect.centery,
                                player.rect.centerx - self.rect.centerx)

        # 发射多条火焰
        for i in range(flame_directions):
            # 计算每条火焰的角度
            if flame_directions > 1:
                angle_spread = math.pi / 4  # 45度扇形范围
                current_angle = base_angle - (angle_spread / 2) + (angle_spread / (flame_directions - 1)) * i
            else:
                current_angle = base_angle

            # 逐步创建火焰粒子
            for dist in range(20, int(flame_range), 20):
                flame_x = self.rect.centerx + math.cos(current_angle) * dist
                flame_y = self.rect.centery + math.sin(current_angle) * dist

                # 添加火焰粒子
                particles.add_particles(flame_x, flame_y, ORANGE, count=5, speed=1, life=40, size=6)

                # 检测玩家是否在火焰路径上
                if math.sqrt((player.rect.centerx - flame_x) ** 2 + (player.rect.centery - flame_y) ** 2) < 30:
                    if not player.is_invincible():
                        player.health -= flame_damage / (dist / 50)  # 距离远伤害降低
                        player.hit = True
                        player.hit_cooldown = 5

    def machine_attack(self, world, player, particles):
        # 机械打击，类似伐木机但更强力
        # 首先从上方掉落模拟机械臂
        drop_points = 5
        machine_damage = self.strength * 0.8

        # 确定打击点，包括玩家当前位置
        drop_positions = [player.rect.centerx]

        # 添加随机点
        for _ in range(drop_points - 1):
            offset = random.randint(-200, 200)
            drop_positions.append(player.rect.centerx + offset)

        # 对每个打击点创建效果和检测伤害
        for drop_x in drop_positions:
            # 创建警告效果
            for y in range(0, 300, 30):
                warning_y = self.rect.centery - y
                particles.add_particles(drop_x, warning_y, RED, count=1, speed=0, life=30, size=8)

            # 检测玩家是否在打击范围内
            if abs(player.rect.centerx - drop_x) < 50 and not player.is_invincible():
                player.health -= machine_damage
                player.hit = True
                player.hit_cooldown = 15

                # 击退效果
                player.velocity_y = -10  # 向上击飞

                # 对森林造成伤害
                world.forest_health -= 2
                if world.forest_health < 0:
                    world.forest_health = 0

            # 创建打击效果
            for _ in range(15):
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-10, 200)
                particles.add_particles(drop_x + offset_x, self.rect.centery + offset_y,
                                        GRAY, count=1, speed=random.uniform(1, 3), life=40, size=random.randint(3, 8))

    def spawn_minions(self, particles):
        # 在BOSS周围产生视觉效果
        particles.add_particles(self.rect.centerx, self.rect.centery, GREEN, count=30, speed=2, size=5)

        # 这里只创建视觉效果，实际的小怪生成应由Game类处理
        # 我们可以设置一个标志让Game类知道需要生成小怪
        self.should_spawn_minions = True
        # self.minion_type = random.randint(0, 3)  # 随机决定召唤的小怪类型

    def enter_phase_two(self, particles):
        # 进入第二阶段的逻辑
        self.phase = 2

        # 增强BOSS能力
        self.speed *= 1.5
        self.attack_range *= 1.2
        self.special_attack_interval = 200  # 更频繁的特殊攻击

        # 视觉效果
        particles.add_particles(self.rect.centerx, self.rect.centery, RED, count=50, speed=3, size=10, life=60)

        # 暂时无敌
        self.hit_cooldown = 60

    def activate_shield(self, particles):
        # 激活护盾
        self.shield_active = True
        self.shield_health = self.shield_max_health

        # 护盾激活效果
        particles.add_particles(self.rect.centerx, self.rect.centery, CYAN, count=40, speed=2, size=7, life=60)

    def draw(self, surface, scroll):
        super().draw(surface, scroll)

        # 如果护盾激活，绘制护盾效果
        if self.shield_active:
            shield_radius = max(self.rect.width, self.rect.height) + 10
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 255, 255, 50), (shield_radius, shield_radius), shield_radius)

            # 在护盾边缘绘制更明显的线条
            pygame.draw.circle(shield_surface, (0, 255, 255, 150), (shield_radius, shield_radius), shield_radius, 3)

            # 绘制护盾
            surface.blit(shield_surface,
                         (self.rect.centerx - shield_radius - scroll[0],
                          self.rect.centery - shield_radius - scroll[1]))

            # 绘制护盾生命条
            shield_bar_width = self.rect.width
            pygame.draw.rect(surface, CYAN,
                             (self.rect.x - scroll[0], self.rect.y - 25 - scroll[1],
                              shield_bar_width, 5))
            pygame.draw.rect(surface, BLUE,
                             (self.rect.x - scroll[0], self.rect.y - 25 - scroll[1],
                              int(shield_bar_width * (self.shield_health / self.shield_max_health)), 5))

        # 在准备特殊攻击时显示视觉提示
        if self.is_preparing_special:
            # 根据攻击类型显示不同颜色的光环
            if self.attack_type == 0:  # 冲击波
                glow_color = YELLOW
            elif self.attack_type == 1:  # 污染
                glow_color = PURPLE
            elif self.attack_type == 2:  # 火焰
                glow_color = ORANGE
            else:  # 机械
                glow_color = GRAY

            # 创建闪烁效果
            alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 100))
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, alpha), (0, 0, self.rect.width + 20, self.rect.height + 20), 5,
                             10)

            # 绘制光环
            surface.blit(glow_surface,
                         (self.rect.x - 10 - scroll[0],
                          self.rect.y - 10 - scroll[1]))

    def take_damage(self, damage, particles):
        # 重写伤害处理函数
        # 如果护盾激活，先扣除护盾生命值
        if self.shield_active:
            self.shield_health -= damage
            particles.add_particles(self.rect.centerx, self.rect.centery, CYAN, count=10, size=3)

            # 检查护盾是否破裂
            if self.shield_health <= 0:
                self.shield_active = False
                self.shield_cooldown = 600  # 10秒护盾冷却时间
                particles.add_particles(self.rect.centerx, self.rect.centery, CYAN, count=30, speed=3, size=6)
                return
        else:
            # 正常受到伤害
            self.health -= damage
            self.hit_cooldown = 5

            # 额外视觉效果
            particles.add_particles(self.rect.centerx, self.rect.centery, RED, count=int(damage / 2), size=4)

            # 检查生命值
            if self.health <= 0:
                self.alive = False
                # 死亡爆炸效果
                for _ in range(5):  # 多次爆炸效果
                    offset_x = random.randint(-30, 30)
                    offset_y = random.randint(-30, 30)
                    particles.add_particles(self.rect.centerx + offset_x, self.rect.centery + offset_y,
                                            RED, count=30, speed=random.uniform(2, 4), size=random.randint(5, 10))