import os
import sys

import pygame
import math
from enum import Enum
from constants import GRAVITY, GREEN, RED, BLUE, PURPLE, BROWN


# 角色类型
class CharacterType(Enum):
    LIA = 0
    KARN = 1

# 资源加载函数
def load_image(name, scale=1, frame=0):
    """
    加载2-bit character generator PNG图片

    参数:
    - name: 图片文件名（如 "lia", "karn"）
    - scale: 缩放比例
    - frame: 动作帧索引 (0-5)
           0: 向前1, 1: 向后1, 2: 向左1
           3: 向前2, 4: 向后2, 5: 向左2

    返回: pygame.Surface 对象
    """

    # 构建图片路径
    if "lia" in name.lower():
        image_path = "images/lia.png"  # 你的lia角色图片路径
    elif "karn" in name.lower():
        image_path = "images/karn.png"  # 你的karn角色图片路径
    elif "enemy" in name.lower():
        image_path = "images/enemy.png"  # 敌人图片路径
    elif "background" in name.lower():
        # 背景图片处理
        img = pygame.Surface((1200, 700))
        img.fill((100, 200, 255))  # 背景用淡蓝色表示
        return img
    else:
        # 其他图片的默认处理
        img = pygame.Surface((16, 16))
        img.fill((200, 200, 200))  # 其他用灰色表示
        if scale != 1:
            width = img.get_width()
            height = img.get_height()
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
        return img

    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"警告: 图片文件 {image_path} 不存在，使用占位符")
            # 创建占位符
            img = pygame.Surface((16, 16))
            if "lia" in name.lower():
                img.fill((0, 200, 100))  # 莉娅用绿色表示
            elif "karn" in name.lower():
                img.fill((150, 75, 0))  # 卡恩用棕色表示
            elif "enemy" in name.lower():
                img.fill((200, 0, 0))  # 敌人用红色表示
        else:
            # 加载完整的精灵表
            sprite_sheet = pygame.image.load(image_path).convert_alpha()

            # 验证图片尺寸
            if sprite_sheet.get_width() != 96 or sprite_sheet.get_height() != 16:
                print(
                    f"警告: 图片 {image_path} 尺寸不是 96x16，实际尺寸: {sprite_sheet.get_width()}x{sprite_sheet.get_height()}")

            # 每个动作帧的宽度是 16 像素 (96/6=16)
            frame_width = 16
            frame_height = 16

            # 确保frame在有效范围内
            frame = max(0, min(frame, 5))

            # 计算要提取的矩形区域
            x = frame * frame_width
            y = 0

            # 创建一个新的surface来存储单个帧
            img = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)

            # 从精灵表中提取指定帧
            source_rect = pygame.Rect(x, y, frame_width, frame_height)
            img.blit(sprite_sheet, (0, 0), source_rect)

    except pygame.error as e:
        print(f"加载图片 {image_path} 时出错: {e}")
        # 创建占位符
        img = pygame.Surface((16, 16))
        if "lia" in name.lower():
            img.fill((0, 200, 100))
        elif "karn" in name.lower():
            img.fill((150, 75, 0))
        elif "enemy" in name.lower():
            img.fill((200, 0, 0))
        else:
            img.fill((200, 200, 200))

    # 应用缩放
    if scale != 1:
        width = img.get_width()
        height = img.get_height()
        img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))

    return img


def load_character_animations(character_name, scale=1):
    """
    加载角色的所有动画帧

    参数:
    - character_name: 角色名称 ("lia" 或 "karn")
    - scale: 缩放比例

    返回: 包含所有动画的列表 [idle, run, jump, attack]
    """

    # 为不同动作映射到对应的帧
    # 0: 向前1(idle), 1: 向后1, 2: 向左1(run_left)
    # 3: 向前2(run_forward), 4: 向后2(jump), 5: 向左2(attack)

    idle_frames = [load_image(character_name, scale, 0)]  # 向前1作为idle
    run_frames = [
        pygame.transform.flip(load_image(character_name, scale, 2), True, False),  # 向左1
        pygame.transform.flip(load_image(character_name, scale, 5), True, False),  # 向左2
    ]
    jump_frames = [pygame.transform.flip(load_image(character_name, scale, 5), True, False)]  # 向左2
    attack_frames = [load_image(character_name, scale, 3)]  # 向前2作为attack

    return [idle_frames, run_frames, jump_frames, attack_frames]


# 角色基类
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, character_type, scale):
        pygame.sprite.Sprite.__init__(self)
        self.character_type = character_type
        self.scale = scale
        self.direction = 1  # 1表示右，-1表示左
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0:闲置, 1:奔跑, 2:跳跃, 3:攻击
        self.update_time = pygame.time.get_ticks()
        
        # 加载动画
        self.load_animations()
        
        # 设置初始图像
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 移动变量
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.jump_cooldown = 0
        
        # 战斗变量
        self.health = 100
        self.max_health = 100
        self.magic = 100
        self.max_magic = 100
        self.magic_regen = 0.05  # 每帧回复的魔法值
        self.alive = True
        self.attack_cooldown = 0
        self.hit = False
        self.hit_cooldown = 0
        self.invulnerability = 0  # 无敌时间
        
        # 技能变量
        self.skill_cooldowns = [0, 0, 0]  # 三个技能的冷却时间
        self.action_timer = 0  # 添加动作计时
    
    def load_animations(self):
        # 这个方法在子类中实现
        pass

    # 修改 Character 类的 move 方法，实现开发者模式下的无敌
    def move(self, moving_left, moving_right, world, enemies, particles, dev_mode=False, score_factor=0):
        # 重置移动变量
        dx = 0
        dy = 0
        speed = min(int(self.speed * (1 + score_factor / 50)), 10)

        # 根据按键确定移动方向
        if moving_left:
            dx = -speed
            self.direction = -1
            self.flip = True

        if moving_right:
            dx = speed
            self.direction = 1
            self.flip = False

        # 跳跃
        if self.jump and not self.in_air and self.jump_cooldown == 0:
            self.velocity_y = -min(int(15 * (1 + score_factor / 200)), 25)
            self.jump = False
            self.in_air = True
            self.jump_cooldown = 20
            particles.add_particles(self.rect.centerx, self.rect.bottom, GREEN, count=15)

        # 应用重力
        self.velocity_y += GRAVITY
        dy += self.velocity_y

        # 检查与世界的碰撞
        for tile in world.tile_list:
            # 检查水平碰撞
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0

            # 检查垂直碰撞
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # 检查是否在跳跃
                if self.velocity_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.velocity_y = 0
                # 检查是否下落
                elif self.velocity_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.velocity_y = 0
                    self.in_air = False

        # 检查是否离开地面
        if not world.tile_collide(self.rect.x, self.rect.y + 1, self.rect.width, self.rect.height):
            self.in_air = True

        # 更新位置
        self.rect.x += dx
        self.rect.y += dy

        # 检查是否掉出世界边界
        if self.rect.y > world.world_height or self.rect.y < -500:
            # 如果角色掉出世界边界，重置到初始位置
            self.reset_to_spawn_point(world)
            # 受到伤害
            if not dev_mode:
                self.health -= 10
                self.hit = True
                self.hit_cooldown = 20

        # 更新冷却时间
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        for i in range(len(self.skill_cooldowns)):
            if self.skill_cooldowns[i] > 0:
                self.skill_cooldowns[i] -= 1

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        if self.invulnerability > 0:
            self.invulnerability -= 1

        # 开发者模式下无限魔法
        if dev_mode:
            self.magic = self.max_magic
        else:
            # 正常模式下回复魔法值
            if self.magic < self.max_magic:
                self.magic += self.magic_regen
                if self.magic > self.max_magic:
                    self.magic = self.max_magic
        # 更新角色动作状态
        if not (self.action == 3 and self.action_timer > 0):
            if self.in_air:
                # 在空中时显示跳跃动作
                self.update_action(2)  # 2: 跳跃动作
            elif moving_left or moving_right:
                # 移动时显示奔跑动作
                self.update_action(1)  # 1: 奔跑动作
            else:
                # 静止时显示闲置动作
                self.update_action(0)  # 0: 闲置动作

    # 添加重置到初始位置的方法
    def reset_to_spawn_point(self, world):
        # 记录角色类别，以便在重生时保持角色类型
        character_class = self.__class__.__name__

        # 重置位置到世界的初始点
        if hasattr(world, 'start_pos') and world.start_pos:
            self.rect.x = world.start_pos[0]
            self.rect.y = world.start_pos[1]
        else:
            # 如果世界没有定义初始点，使用默认值（世界左上角附近）
            self.rect.x = 100
            self.rect.y = 100

        # 重置速度
        self.velocity_y = 0

        # 重置在空中的状态
        self.in_air = True

        # 如果是倒计时要显示重生效果，可以添加无敌时间
        self.invulnerability = 60  # 给予1秒无敌时间

    def update_animation(self):
        # 根据角色动作更新动画
        ANIMATION_COOLDOWN = 100

        # 处理攻击动作的持续时间
        if self.action == 3 and self.action_timer > 0:  # 攻击动作
            self.action_timer -= 1
            if self.action_timer <= 0:
                # 攻击动作结束，切换回闲置状态
                self.update_action(0)

        # 更新图像
        self.image = self.animation_list[self.action][self.frame_index]

        # 检查是否需要更新动画帧
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # 如果动画结束则重置
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
    
    def update_action(self, new_action):
        # 检查新动作是否与当前动作不同
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def attack(self, enemies, particles, dev_mode=False, score_factor=0):
        # 基础攻击
        if self.attack_cooldown == 0:
            self.attack_cooldown = 20
            attacking_rect = pygame.Rect(self.rect.centerx + (2 * self.rect.width * self.direction), self.rect.y,
                                         2 * self.rect.width, self.rect.height)

            # 切换到攻击动作
            self.update_action(3)  # 3: 攻击动作
            self.action_timer = 15  # 攻击动作持续15帧
            # 检查是否击中敌人
            for enemy in enemies:
                if attacking_rect.colliderect(enemy.rect) and enemy.alive:
                    # 开发者模式下秒杀敌人
                    if dev_mode:
                        enemy.health = 0
                    else:
                        if not enemy.shield_active:
                            enemy.health -= int(20 * (1+score_factor/100))
                        else:
                            enemy.take_damage(int(20 * (1+score_factor/100)), particles)
                    enemy.hit = True
                    enemy.hit_cooldown = 10
                    particles.add_particles(enemy.rect.centerx, enemy.rect.centery, RED)

            particles.add_particles(self.rect.centerx + 30 * self.direction, self.rect.centery, GREEN)


    # 为 Character 类添加一个方法，检查是否处于开发者模式下的无敌状态
    def is_invincible(self):

        # 正常情况下检查无敌时间
        return self.invulnerability > 0


    def draw(self, surface, scroll):
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        # src = (32*4, 0, 16*4, 16*4)
        # surface.blit(flipped_image, (self.rect.x - scroll[0], self.rect.y - scroll[1]), src)
        surface.blit(flipped_image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        
        # 绘制生命条
        pygame.draw.rect(surface, RED, (self.rect.x - scroll[0], self.rect.y - 20 - scroll[1], self.rect.width, 10))
        if self.health > 0:
            pygame.draw.rect(surface, GREEN, 
                            (self.rect.x - scroll[0], self.rect.y - 20 - scroll[1], 
                             int(self.rect.width * (self.health/self.max_health)), 10))
        
        # 闪烁效果（受伤时）
        if self.hit_cooldown > 0:
            alpha = self.hit_cooldown * 25
            hit_surface = pygame.Surface((self.rect.width, self.rect.height))
            hit_surface.fill((255, 0, 0))
            hit_surface.set_alpha(alpha)
            surface.blit(hit_surface, (self.rect.x - scroll[0], self.rect.y - scroll[1]))



class Lia(Character):
    def __init__(self, x, y, scale):
        super().__init__(x, y, CharacterType.LIA, scale)
        self.speed = 5
        self.health = 80
        self.max_health = 80
        self.magic = 150
        self.max_magic = 150
        self.magic_regen = 0.4
        self.skill_costs = [20, 30, 40]  # 三个技能的魔法消耗

    # 修改后的Lia类的load_animations方法
    def load_animations(self):
        """莉娅角色的动画加载"""
        self.animation_list = load_character_animations("lia", self.scale)

    def skill_1(self, enemies, particles, score_factor=0):
        # 藤蔓缠绕 - 修改为暂时减速且不叠加
        if self.skill_cooldowns[0] == 0 and self.magic >= self.skill_costs[0]:
            self.skill_cooldowns[0] = 60  # 1秒冷却
            self.magic -= self.skill_costs[0]

            # 检测范围内的敌人
            skill_range = 200
            slow_duration = 120  # 减速持续2秒(120帧)
            slow_factor = 0.5  # 减速至原速度的50%

            for enemy in enemies:
                dist = math.sqrt((enemy.rect.centerx - self.rect.centerx) ** 2 +
                                 (enemy.rect.centery - self.rect.centery) ** 2)
                if dist <= skill_range and enemy.alive:
                    # 使用新方法应用减速效果
                    enemy.apply_slow(slow_factor, slow_duration)
                    enemy.hit = True
                    enemy.hit_cooldown = 5
                    particles.add_particles(enemy.rect.centerx, enemy.rect.centery, GREEN, count=30)

            return True
        return False

    def skill_2(self, world, particles, score_factor):
        # 治愈之触
        if self.skill_cooldowns[1] == 0 and self.magic >= self.skill_costs[1]:
            self.skill_cooldowns[1] = 120  # 2秒冷却
            self.magic -= self.skill_costs[1]

            # 回复生命值
            heal_amount = int(30 * (1+score_factor/10))
            self.health += heal_amount
            if self.health > self.max_health:
                self.health = self.max_health

            # 增加森林健康度
            world.forest_health += int(1 * (1+score_factor/10))
            if world.forest_health > 100:
                world.forest_health = 100

            particles.add_particles(self.rect.centerx, self.rect.centery, BLUE, count=40, size=8)
            return True
        return False

    def skill_3(self, enemies, particles, score_factor):
        # 花朵陷阱
        if self.skill_cooldowns[2] == 0 and self.magic >= self.skill_costs[2]:
            self.skill_cooldowns[2] = 180  # 3秒冷却
            self.magic -= self.skill_costs[2]

            # 在角色前方一定距离创建陷阱
            trap_x = self.rect.centerx + 100 * self.direction
            trap_y = self.rect.bottom

            # 检测进入陷阱范围的敌人
            trap_rect = pygame.Rect(trap_x - 50, trap_y - 50, 100, 100)
            slow_duration = 180  # 减速持续3秒(180帧)
            slow_factor = 0.3  # 减速至原速度的30%

            for enemy in enemies:
                if trap_rect.colliderect(enemy.rect) and enemy.alive:
                    # 使用新方法应用减速效果
                    enemy.apply_slow(slow_factor, slow_duration)
                    enemy.health -= int(15 * (1+score_factor/10))
                    enemy.hit = True
                    enemy.hit_cooldown = 15

            particles.add_particles(trap_x, trap_y, PURPLE, count=50, size=6)
            return True
        return False


class Karn(Character):
    def __init__(self, x, y, scale):
        super().__init__(x, y, CharacterType.KARN, scale)
        self.speed = 3
        self.health = 150
        self.max_health = 150
        self.magic = 80
        self.max_magic = 80
        self.magic_regen = 0.2
        self.skill_costs = [15, 25, 35]  # 三个技能的魔法消耗

    def load_animations(self):
        """角色的动画加载"""
        self.animation_list = load_character_animations("karn", self.scale)
    
    def skill_1(self, enemies, particles, score_factor):
        # 大地震击
        if self.skill_cooldowns[0] == 0 and self.magic >= self.skill_costs[0]:
            self.skill_cooldowns[0] = 90  # 1.5秒冷却
            self.magic -= self.skill_costs[0]
            
            # 攻击范围内的所有敌人
            skill_range = 150
            for enemy in enemies:
                dist = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                                (enemy.rect.centery - self.rect.centery)**2)
                if dist <= skill_range and enemy.alive:
                    enemy.health -= int(30 * (1+score_factor/10))
                    enemy.hit = True
                    enemy.hit_cooldown = 15
                    enemy.velocity_y = -5  # 击退效果
            
            particles.add_particles(self.rect.centerx, self.rect.bottom, BROWN, count=40, size=8)
            return True
        return False
    
    def skill_2(self, particles, score_factor):
        # 树皮护甲
        if self.skill_cooldowns[1] == 0 and self.magic >= self.skill_costs[1]:
            self.skill_cooldowns[1] = 150  # 2.5秒冷却
            self.magic -= self.skill_costs[1]
            
            # 提高防御力（通过临时无敌实现）
            self.invulnerability = int(180 * (1+score_factor/100))  # 3秒无敌
            
            particles.add_particles(self.rect.centerx, self.rect.centery, BROWN, count=30)
            return True
        return False
    
    def skill_3(self, particles, score_factor):
        # 根系束缚
        if self.skill_cooldowns[2] == 0 and self.magic >= self.skill_costs[2]:
            self.skill_cooldowns[2] = 210  # 3.5秒冷却
            self.magic -= self.skill_costs[2]
            
            # 固定位置并恢复魔法
            self.magic += self.max_magic * 0.5
            if self.magic > self.max_magic:
                self.magic = self.max_magic
            
            particles.add_particles(self.rect.centerx, self.rect.bottom, GREEN, count=50, size=4, life=60)
            return True
        return False