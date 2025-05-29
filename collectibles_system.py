#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random
import math
from enum import Enum
from constants import *


class CollectibleType(Enum):
    """收集品类型枚举"""
    SEED = "seed"                    # 种子 - 恢复森林健康
    CRYSTAL = "crystal"              # 能量水晶 - 恢复魔法值
    BERRY = "berry"                  # 浆果 - 恢复生命值
    FLOWER = "flower"                # 花朵 - 装饰收集品
    LEAF = "leaf"                    # 叶子 - 经验值提升
    MUSHROOM = "mushroom"            # 蘑菇 - 临时能力提升
    COIN = "coin"                    # 金币 - 游戏货币
    ARTIFACT = "artifact"            # 古代神器 - 稀有收集品
    POTION = "potion"               # 药水 - 各种效果


class CollectibleRarity(Enum):
    """收集品稀有度"""
    COMMON = 1      # 普通 - 白色
    UNCOMMON = 2    # 不常见 - 绿色
    RARE = 3        # 稀有 - 蓝色
    EPIC = 4        # 史诗 - 紫色
    LEGENDARY = 5   # 传说 - 金色


class Collectible:
    """收集品基类"""
    
    def __init__(self, x, y, collectible_type, rarity=CollectibleRarity.COMMON):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.collectible_type = collectible_type
        self.rarity = rarity
        self.collected = False
        self.active = True
        
        # 动画相关
        self.float_offset = 0
        self.float_speed = 2
        self.rotation = 0
        self.rotation_speed = 3
        self.scale = 1.0
        self.pulse_timer = 0
        
        # 发光效果
        self.glow_radius = 20
        self.glow_alpha = 100
        
        # 磁性吸引效果
        self.magnetic_range = 80
        self.attracted = False
        self.attract_speed = 5
        
        # 根据类型和稀有度设置属性
        self._set_properties()
        
        # 生成随机的浮动相位，避免所有物品同步浮动
        self.float_phase = random.uniform(0, math.pi * 2)
        
    def _set_properties(self):
        """根据类型和稀有度设置收集品属性"""
        # 基础颜色映射
        type_colors = {
            CollectibleType.SEED: (139, 69, 19),        # 棕色
            CollectibleType.CRYSTAL: (0, 191, 255),     # 蓝色
            CollectibleType.BERRY: (220, 20, 60),       # 红色
            CollectibleType.FLOWER: (255, 105, 180),    # 粉色
            CollectibleType.LEAF: (34, 139, 34),        # 绿色
            CollectibleType.MUSHROOM: (160, 82, 45),    # 褐色
            CollectibleType.COIN: (255, 215, 0),        # 金色
            CollectibleType.ARTIFACT: (128, 0, 128),    # 紫色
            CollectibleType.POTION: (50, 205, 50)       # 青绿色
        }
        
        # 稀有度颜色调整
        rarity_multipliers = {
            CollectibleRarity.COMMON: 1.0,
            CollectibleRarity.UNCOMMON: 1.1,
            CollectibleRarity.RARE: 1.2,
            CollectibleRarity.EPIC: 1.3,
            CollectibleRarity.LEGENDARY: 1.5
        }
        
        base_color = type_colors.get(self.collectible_type, (255, 255, 255))
        multiplier = rarity_multipliers[self.rarity]
        
        # 应用稀有度调整
        self.color = tuple(min(255, int(c * multiplier)) for c in base_color)
        
        # 稀有度边框颜色
        self.border_color = {
            CollectibleRarity.COMMON: (200, 200, 200),      # 灰色
            CollectibleRarity.UNCOMMON: (0, 255, 0),        # 绿色
            CollectibleRarity.RARE: (0, 112, 255),          # 蓝色
            CollectibleRarity.EPIC: (163, 53, 238),         # 紫色
            CollectibleRarity.LEGENDARY: (255, 215, 0)      # 金色
        }[self.rarity]
        
        # 设置收集效果值
        self._set_effect_values()
        
    def _set_effect_values(self):
        """设置收集品的效果数值"""
        rarity_multiplier = self.rarity.value
        
        self.effects = {}
        
        if self.collectible_type == CollectibleType.SEED:
            self.effects['forest_health'] = 10 * rarity_multiplier
        elif self.collectible_type == CollectibleType.CRYSTAL:
            self.effects['magic'] = 15 * rarity_multiplier
        elif self.collectible_type == CollectibleType.BERRY:
            self.effects['health'] = 20 * rarity_multiplier
        elif self.collectible_type == CollectibleType.FLOWER:
            self.effects['score'] = 50 * rarity_multiplier
        elif self.collectible_type == CollectibleType.LEAF:
            self.effects['experience'] = 25 * rarity_multiplier
        elif self.collectible_type == CollectibleType.MUSHROOM:
            self.effects['temp_boost'] = {'type': 'speed', 'value': 1.5, 'duration': 300}
        elif self.collectible_type == CollectibleType.COIN:
            self.effects['coins'] = 5 * rarity_multiplier
        elif self.collectible_type == CollectibleType.ARTIFACT:
            self.effects['score'] = 200 * rarity_multiplier
            self.effects['all_stats'] = 5 * rarity_multiplier
        elif self.collectible_type == CollectibleType.POTION:
            potion_effects = ['health', 'magic', 'speed', 'strength']
            effect_type = random.choice(potion_effects)
            if effect_type in ['health', 'magic']:
                self.effects[effect_type] = 30 * rarity_multiplier
            else:
                self.effects['temp_boost'] = {
                    'type': effect_type, 
                    'value': 1.3 + (0.1 * rarity_multiplier), 
                    'duration': 600
                }
    
    def update(self, player=None, particle_system=None):
        """更新收集品状态"""
        if not self.active or self.collected:
            return
            
        # 浮动动画
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003 + self.float_phase) * 5
        
        # 旋转动画
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
            
        # 脉冲效果
        self.pulse_timer += 1
        self.scale = 1.0 + math.sin(self.pulse_timer * 0.1) * 0.1
        
        # 发光效果变化
        self.glow_alpha = 80 + math.sin(self.pulse_timer * 0.05) * 40
        
        # 检查磁性吸引
        if player:
            distance = math.sqrt((self.rect.centerx - player.rect.centerx)**2 + 
                               (self.rect.centery - player.rect.centery)**2)
            
            if distance < self.magnetic_range:
                self.attracted = True
                # 向玩家移动
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                
                if distance > 0:
                    move_x = (dx / distance) * self.attract_speed
                    move_y = (dy / distance) * self.attract_speed
                    self.rect.x += move_x
                    self.rect.y += move_y
                    
                # 创建吸引粒子效果
                if particle_system and random.randint(1, 5) == 1:
                    particle_system.create_attract_particle(
                        self.rect.centerx, self.rect.centery, 
                        player.rect.centerx, player.rect.centery
                    )
                    
            # 检查收集
            if distance < 25:  # 收集范围
                self.collect(player, particle_system)

    def collect(self, player, particle_system=None):
        """收集物品 - 增强版本显示收集信息"""
        if self.collected:
            return False

        self.collected = True
        self.active = False

        # 应用效果
        applied_effects = self._apply_effects(player)

        # 创建收集粒子效果
        if particle_system:
            particle_system.create_collect_effect(
                self.rect.centerx, self.rect.centery,
                self.color, self.rarity.value
            )

            # 创建文字提示粒子
            # rarity_names = {1: '普通', 2: '不常见', 3: '稀有', 4: '史诗', 5: '传说'}
            # collect_text = f"+{rarity_names[self.rarity.value]}{self.collectible_type.value}"
            # particle_system.create_text_particle(
            #     self.rect.centerx, self.rect.centery - 20,
            #     collect_text, self.border_color
            # )

        return True

    def _apply_effects(self, player):
        """应用收集品效果到玩家"""
        for effect_type, value in self.effects.items():
            if effect_type == 'health':
                player.health = min(player.max_health, player.health + value)
            elif effect_type == 'magic':
                player.magic = min(player.max_magic, player.magic + value)
            elif effect_type == 'forest_health' and hasattr(player, 'world'):
                if player.world:
                    player.world.forest_health = min(100, player.world.forest_health + value)
            elif effect_type == 'experience':
                if hasattr(player, 'experience'):
                    player.experience += value
            elif effect_type == 'coins':
                if hasattr(player, 'coins'):
                    player.coins += value
                else:
                    player.coins = value
            elif effect_type == 'score':
                if hasattr(player, 'score'):
                    player.score += value
                else:
                    player.score = value
            elif effect_type == 'temp_boost':
                self._apply_temporary_boost(player, value)
            elif effect_type == 'all_stats':
                # 全属性小幅提升
                player.health = min(player.max_health, player.health + value)
                player.magic = min(player.max_magic, player.magic + value)
    
    def _apply_temporary_boost(self, player, boost_info):
        """应用临时增益效果"""
        if not hasattr(player, 'active_boosts'):
            player.active_boosts = []
            
        boost = {
            'type': boost_info['type'],
            'value': boost_info['value'],
            'duration': boost_info['duration'],
            'timer': boost_info['duration']
        }
        
        player.active_boosts.append(boost)
    
    def draw(self, screen, scroll):
        """绘制收集品"""
        if not self.active or self.collected:
            return
            
        # 计算绘制位置
        draw_x = self.rect.x - scroll[0]
        draw_y = self.rect.y - scroll[1] + self.float_offset
        
        # 绘制发光效果
        if self.rarity.value > 1:
            glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2))
            glow_surface.set_alpha(self.glow_alpha)
            pygame.draw.circle(glow_surface, self.border_color,
                             (self.glow_radius, self.glow_radius), self.glow_radius)
            screen.blit(glow_surface, (draw_x - self.glow_radius + 16, 
                                     draw_y - self.glow_radius + 16))
        
        # 绘制主体
        scaled_size = int(32 * self.scale)
        offset = (32 - scaled_size) // 2
        
        # 绘制边框（稀有度颜色）
        border_rect = pygame.Rect(draw_x + offset - 2, draw_y + offset - 2, 
                                 scaled_size + 4, scaled_size + 4)
        pygame.draw.rect(screen, self.border_color, border_rect, 2)
        
        # 绘制主体
        main_rect = pygame.Rect(draw_x + offset, draw_y + offset, scaled_size, scaled_size)
        pygame.draw.rect(screen, self.color, main_rect)
        
        # 绘制类型标识
        self._draw_type_icon(screen, draw_x + 16, draw_y + 16)
        
        # 绘制稀有度星星
        if self.rarity.value > 1:
            self._draw_rarity_stars(screen, draw_x, draw_y - 15)
    
    def _draw_type_icon(self, screen, center_x, center_y):
        """绘制类型图标"""
        icon_color = (255, 255, 255)
        
        if self.collectible_type == CollectibleType.SEED:
            # 绘制种子图标
            pygame.draw.circle(screen, icon_color, (center_x, center_y), 3)
            pygame.draw.line(screen, icon_color, (center_x, center_y-3), (center_x, center_y-8), 2)
        elif self.collectible_type == CollectibleType.CRYSTAL:
            # 绘制水晶图标
            points = [(center_x, center_y-6), (center_x-4, center_y), 
                     (center_x, center_y+6), (center_x+4, center_y)]
            pygame.draw.polygon(screen, icon_color, points)
        elif self.collectible_type == CollectibleType.BERRY:
            # 绘制浆果图标
            pygame.draw.circle(screen, icon_color, (center_x, center_y), 4)
            pygame.draw.circle(screen, icon_color, (center_x-2, center_y-2), 2)
        elif self.collectible_type == CollectibleType.FLOWER:
            # 绘制花朵图标
            for angle in range(0, 360, 60):
                x = center_x + int(3 * math.cos(math.radians(angle)))
                y = center_y + int(3 * math.sin(math.radians(angle)))
                pygame.draw.circle(screen, icon_color, (x, y), 2)
        elif self.collectible_type == CollectibleType.COIN:
            # 绘制金币图标
            pygame.draw.circle(screen, icon_color, (center_x, center_y), 5, 2)
            pygame.draw.line(screen, icon_color, (center_x-2, center_y), (center_x+2, center_y), 2)
    
    def _draw_rarity_stars(self, screen, x, y):
        """绘制稀有度星星"""
        star_color = self.border_color
        for i in range(min(5, self.rarity.value)):
            star_x = x + i * 8
            # 简单的星星形状
            pygame.draw.circle(screen, star_color, (star_x, y), 2)


class CollectibleManager:
    """收集品管理器"""
    
    def __init__(self):
        self.collectibles = []
        self.collection_stats = {
            'total_collected': 0,
            'by_type': {ctype: 0 for ctype in CollectibleType},
            'by_rarity': {rarity: 0 for rarity in CollectibleRarity},
            'coins': 0,
            'score': 0
        }
        
    def spawn_collectible(self, x, y, collectible_type=None, rarity=None):
        """生成收集品"""
        if collectible_type is None:
            collectible_type = random.choice(list(CollectibleType))
            
        if rarity is None:
            # 稀有度概率分布
            rarity_chances = [60, 25, 10, 4, 1]  # 普通, 不常见, 稀有, 史诗, 传说
            rarity_roll = random.randint(1, 100)
            
            if rarity_roll <= rarity_chances[0]:
                rarity = CollectibleRarity.COMMON
            elif rarity_roll <= sum(rarity_chances[:2]):
                rarity = CollectibleRarity.UNCOMMON
            elif rarity_roll <= sum(rarity_chances[:3]):
                rarity = CollectibleRarity.RARE
            elif rarity_roll <= sum(rarity_chances[:4]):
                rarity = CollectibleRarity.EPIC
            else:
                rarity = CollectibleRarity.LEGENDARY
                
        collectible = Collectible(x, y, collectible_type, rarity)
        self.collectibles.append(collectible)
        return collectible
    
    def spawn_level_collectibles(self, level, world_width=1000):
        """为关卡生成收集品"""
        # 清空现有收集品
        self.collectibles = []
        
        # 基础收集品数量
        base_count = 5 + level * 2
        
        # 生成常规收集品
        for _ in range(base_count):
            x = random.randint(100, world_width - 100)
            y = random.randint(400, 500)
            self.spawn_collectible(x, y)
            
        # 生成特殊收集品
        special_count = max(1, level // 2)
        for _ in range(special_count):
            x = random.randint(100, world_width - 100)
            y = random.randint(400, 500)
            special_types = [CollectibleType.ARTIFACT, CollectibleType.POTION]
            special_type = random.choice(special_types)
            rarity = random.choice([CollectibleRarity.RARE, CollectibleRarity.EPIC])
            self.spawn_collectible(x, y, special_type, rarity)
    
    def update(self, player, particle_system=None):
        """更新所有收集品"""
        for collectible in self.collectibles[:]:  # 使用切片来避免修改列表时的问题
            if collectible.active:
                collectible.update(player, particle_system)
                
                # 检查是否被收集
                if collectible.collected:
                    self._update_stats(collectible)
                    
            # 移除已收集的物品
            if collectible.collected:
                self.collectibles.remove(collectible)
    
    def _update_stats(self, collectible):
        """更新收集统计"""
        self.collection_stats['total_collected'] += 1
        self.collection_stats['by_type'][collectible.collectible_type] += 1
        self.collection_stats['by_rarity'][collectible.rarity] += 1
        
        # 更新特殊统计
        if 'coins' in collectible.effects:
            self.collection_stats['coins'] += collectible.effects['coins']
        if 'score' in collectible.effects:
            self.collection_stats['score'] += collectible.effects['score']
    
    def draw(self, screen, scroll):
        """绘制所有收集品"""
        for collectible in self.collectibles:
            collectible.draw(screen, scroll)
    
    def get_collection_progress(self):
        """获取收集进度"""
        total_spawned = len(self.collectibles) + self.collection_stats['total_collected']
        if total_spawned == 0:
            return 0
        return (self.collection_stats['total_collected'] / total_spawned) * 100
    
    def clear_all(self):
        """清空所有收集品"""
        self.collectibles = []
        
    def get_nearby_collectibles(self, x, y, radius=100):
        """获取附近的收集品"""
        nearby = []
        for collectible in self.collectibles:
            if collectible.active:
                distance = math.sqrt((collectible.rect.centerx - x)**2 + 
                                   (collectible.rect.centery - y)**2)
                if distance <= radius:
                    nearby.append(collectible)
        return nearby

    def get_collection_summary(self):
        """获取收集摘要信息"""
        total_spawned = len(self.collectibles) + self.collection_stats['total_collected']

        summary = {
            'total_collected': self.collection_stats['total_collected'],
            'total_spawned': total_spawned,
            'progress_percentage': self.get_collection_progress(),
            'coins': self.collection_stats['coins'],
            'score': self.collection_stats['score'],
            'rare_items': sum(count for rarity, count in self.collection_stats['by_rarity'].items()
                              if rarity.value >= 3),  # 稀有及以上
            'legendary_items': self.collection_stats['by_rarity'].get(
                next(r for r in CollectibleRarity if r.value == 5), 0
            )
        }

        return summary

    def get_achievement_progress(self):
        """获取成就进度"""
        achievements = {
            'collector': {
                'name': '收集家',
                'description': '收集100个物品',
                'progress': min(100, self.collection_stats['total_collected']),
                'target': 100,
                'completed': self.collection_stats['total_collected'] >= 100
            },
            'treasure_hunter': {
                'name': '寻宝者',
                'description': '收集10个稀有物品',
                'progress': min(10, sum(count for rarity, count in self.collection_stats['by_rarity'].items()
                                        if rarity.value >= 3)),
                'target': 10,
                'completed': sum(count for rarity, count in self.collection_stats['by_rarity'].items()
                                 if rarity.value >= 3) >= 10
            },
            'wealthy': {
                'name': '富有者',
                'description': '收集1000金币',
                'progress': min(1000, self.collection_stats['coins']),
                'target': 1000,
                'completed': self.collection_stats['coins'] >= 1000
            }
        }

        return achievements