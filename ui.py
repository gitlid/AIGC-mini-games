#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame

from characters import load_image
from constants import *
from enum import Enum

# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, font, color=(200, 200, 200), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
    
    def draw(self, surface):
        # 绘制按钮
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)  # 黑色边框
        
        # 绘制文本
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def is_clicked(self, pos, event):
        if self.rect.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True
        return False

# 游戏UI类
class GameUI:
    def __init__(self, player):
        self.player = player
        
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large
        
        # 技能图标
        self.skill_icons = []
        self.init_skill_icons()
        
        # 暂停按钮
        self.pause_button = Button(SCREEN_WIDTH - 60, 20, 40, 40, "II", self.font_medium)
        
        # 技能提示信息
        self.skill_tooltips = []
        self.init_skill_tooltips()
        
        # 当前显示的提示
        self.active_tooltip = None
        self.tooltip_timer = 0

        # 添加收集信息显示区域
        self.show_collection_details = False
        self.collection_toggle_button = Button(SCREEN_WIDTH - 250, 20, 180, 40, "收集统计", font_small)

    def draw_detailed_collection_stats(self, screen, stats):
        """绘制详细收集统计"""
        detail_x = 20
        detail_y = 150

        # 背景框
        detail_bg = pygame.Rect(detail_x - 10, detail_y - 5, 300, 350)
        pygame.draw.rect(screen, (0, 0, 0, 200), detail_bg)
        pygame.draw.rect(screen, (100, 100, 100), detail_bg, 2)

        # 标题
        title_text = font_medium.render("详细收集统计", True, WHITE)
        screen.blit(title_text, (detail_x, detail_y))

        current_y = detail_y + 30

        # 按类型统计
        type_title = font_small.render("按类型:", True, (200, 200, 200))
        screen.blit(type_title, (detail_x, current_y))
        current_y += 20

        type_colors = {
            'SEED': (139, 69, 19),
            'CRYSTAL': (0, 191, 255),
            'BERRY': (220, 20, 60),
            'FLOWER': (255, 105, 180),
            'LEAF': (34, 139, 34),
            'MUSHROOM': (160, 82, 45),
            'COIN': (255, 215, 0),
            'ARTIFACT': (128, 0, 128),
            'POTION': (50, 205, 50)
        }

        for ctype, count in stats['by_type'].items():
            if count > 0:
                type_name = ctype.value
                color = type_colors.get(ctype.name, WHITE)
                type_text = font_small.render(f"  {type_name}: {count}", True, color)
                screen.blit(type_text, (detail_x + 10, current_y))
                current_y += 18

        current_y += 10

        # 按稀有度统计
        rarity_title = font_small.render("按稀有度:", True, (200, 200, 200))
        screen.blit(rarity_title, (detail_x, current_y))
        current_y += 20

        rarity_colors = {
            'COMMON': (200, 200, 200),
            'UNCOMMON': (0, 255, 0),
            'RARE': (0, 112, 255),
            'EPIC': (163, 53, 238),
            'LEGENDARY': (255, 215, 0)
        }

        rarity_names = {
            'COMMON': '普通',
            'UNCOMMON': '不常见',
            'RARE': '稀有',
            'EPIC': '史诗',
            'LEGENDARY': '传说'
        }

        for rarity, count in stats['by_rarity'].items():
            if count > 0:
                rarity_name = rarity_names.get(rarity.name, rarity.name)
                color = rarity_colors.get(rarity.name, WHITE)
                rarity_text = font_small.render(f"  {rarity_name}: {count}", True, color)
                screen.blit(rarity_text, (detail_x + 10, current_y))
                current_y += 18


    def draw_collection_status(self, screen, collection_manager):
        """绘制收集系统状态"""
        stats = collection_manager.collection_stats

        # 基础收集信息 - 右上角显示
        info_x = SCREEN_WIDTH - 250
        info_y = 70

        # 背景框
        info_bg = pygame.Rect(info_x - 10, info_y - 5, 240, 120)
        pygame.draw.rect(screen, (0, 0, 0, 180), info_bg)
        pygame.draw.rect(screen, (100, 100, 100), info_bg, 2)

        # 总收集数量
        total_text = font_small.render(f"总收集: {stats['total_collected']}", True, WHITE)
        screen.blit(total_text, (info_x, info_y))

        # 金币数量
        coins_text = font_small.render(f"金币: {stats['coins']}", True, (255, 215, 0))
        screen.blit(coins_text, (info_x, info_y + 20))

        # 分数
        score_text = font_small.render(f"分数: {stats['score']}", True, (0, 255, 0))
        screen.blit(score_text, (info_x, info_y + 40))

        # 收集进度
        progress = collection_manager.get_collection_progress()
        progress_text = font_small.render(f"进度: {progress:.1f}%", True, WHITE)
        screen.blit(progress_text, (info_x, info_y + 60))

        # 进度条
        progress_bar_rect = pygame.Rect(info_x, info_y + 80, 200, 10)
        pygame.draw.rect(screen, (50, 50, 50), progress_bar_rect)
        if progress > 0:
            fill_width = int(200 * (progress / 100))
            fill_rect = pygame.Rect(info_x, info_y + 80, fill_width, 10)
            pygame.draw.rect(screen, (0, 255, 0), fill_rect)
        pygame.draw.rect(screen, WHITE, progress_bar_rect, 1)

        # 详细统计（可切换显示）
        if self.show_collection_details:
            self.draw_detailed_collection_stats(screen, stats)

    def draw_nearby_collectibles_indicator(self, screen, player, collection_manager):
        """显示附近收集品指示器"""
        nearby = collection_manager.get_nearby_collectibles(
            player.rect.centerx, player.rect.centery, 150
        )

        if nearby:
            # 在屏幕左下角显示附近收集品数量
            indicator_text = font_small.render(f"附近收集品: {len(nearby)}", True, (255, 255, 0))
            screen.blit(indicator_text, (500, SCREEN_HEIGHT - 60))

            # 显示最近的收集品类型和稀有度
            if len(nearby) > 0:
                closest = min(nearby, key=lambda c:
                ((c.rect.centerx - player.rect.centerx) ** 2 +
                 (c.rect.centery - player.rect.centery) ** 2) ** 0.5)

                type_name = closest.collectible_type.value
                rarity_name = {
                    1: '普通', 2: '不常见', 3: '稀有', 4: '史诗', 5: '传说'
                }[closest.rarity.value]

                closest_text = font_small.render(
                    f"最近: {rarity_name}{type_name}", True, closest.border_color
                )
                screen.blit(closest_text, (500, SCREEN_HEIGHT - 40))

    def handle_collection_ui_events(self, event, mouse_pos):
        """处理收集UI事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.collection_toggle_button.is_clicked(mouse_pos, event):
                self.show_collection_details = not self.show_collection_details
                return "toggle_collection_details"

        if event.type == pygame.MOUSEMOTION:
            self.collection_toggle_button.check_hover(mouse_pos)

        return None

    def draw(self, screen, collection_manager=None):
        """更新的绘制方法，包含收集信息"""
        # 绘制玩家状态
        self.draw_player_status(screen)

        # 绘制技能图标
        self.draw_skill_icons(screen)

        # 绘制暂停按钮
        self.pause_button.draw(screen)

        # 绘制当前提示信息
        if self.active_tooltip is not None:
            self.draw_tooltip(screen)

        # 绘制收集统计切换按钮
        self.collection_toggle_button.draw(screen)

        # 绘制收集状态
        if collection_manager:
            self.draw_collection_status(screen, collection_manager)
            self.draw_nearby_collectibles_indicator(screen, self.player, collection_manager)

    def init_skill_icons(self):
        # 创建技能图标
        for i in range(3):
            icon = pygame.Surface((50, 50))
            if self.player.character_type == CharacterType.LIA:
                color = (0, 200, 100) if i == 0 else (0, 100, 200) if i == 1 else (128, 0, 128)
            else:  # KARN
                color = (139, 69, 19) if i == 0 else (101, 67, 33) if i == 1 else (0, 100, 0)
            
            icon.fill(color)
            
            # 创建图标对象
            icon_rect = pygame.Rect(50 + i * 60, SCREEN_HEIGHT - 70, 50, 50)
            cooldown = self.player.skill_cooldowns[i]
            max_cooldown = 60 if i == 0 else 120 if i == 1 else 180
            cost = self.player.skill_costs[i]
            
            self.skill_icons.append({
                "surface": icon,
                "rect": icon_rect,
                "cooldown": cooldown,
                "max_cooldown": max_cooldown,
                "cost": cost,
                "key": str(i + 1)  # 对应的按键
            })
    
    def init_skill_tooltips(self):
        # 创建技能提示信息
        if self.player.character_type == CharacterType.LIA:
            self.skill_tooltips = [
                "藤蔓缠绕: 减缓敌人速度",
                "治愈之触: 恢复生命和森林健康",
                "花朵陷阱: 设置陷阱减缓敌人速度并造成伤害"
            ]
        else:  # KARN
            self.skill_tooltips = [
                "大地震击: 对范围内敌人造成伤害",
                "树皮护甲: 暂时提高防御力",
                "根系束缚: 固定位置并恢复魔法能量"
            ]
    
    def update(self):
        # 更新技能图标的冷却时间
        for i, icon in enumerate(self.skill_icons):
            icon["cooldown"] = self.player.skill_cooldowns[i]
        
        # 更新提示信息计时器
        if self.active_tooltip is not None:
            self.tooltip_timer -= 1
            if self.tooltip_timer <= 0:
                self.active_tooltip = None
    
    def show_tooltip(self, index):
        self.active_tooltip = index
        self.tooltip_timer = 120  # 显示2秒
    
    # def draw(self, surface):
    #     # 绘制玩家状态
    #     self.draw_player_status(surface)
    #
    #     # 绘制技能图标
    #     self.draw_skill_icons(surface)
    #
    #     # 绘制暂停按钮
    #     self.pause_button.draw(surface)
    #
    #     # 绘制当前提示信息
    #     if self.active_tooltip is not None:
    #         self.draw_tooltip(surface)
    #
    def draw_player_status(self, surface):
        # 绘制玩家生命条
        pygame.draw.rect(surface, RED, (20, 20, 200, 20))
        if self.player.health > 0:
            pygame.draw.rect(surface, GREEN, 
                           (20, 20, int(200 * (self.player.health/self.player.max_health)), 20))
        
        health_text = self.font_small.render(f"{int(self.player.health)}/{self.player.max_health}", True, WHITE)
        surface.blit(health_text, (25, 20))
        
        # 绘制玩家魔法条
        pygame.draw.rect(surface, (100, 100, 100), (20, 45, 200, 15))
        if self.player.magic > 0:
            pygame.draw.rect(surface, BLUE, 
                           (20, 45, int(200 * (self.player.magic/self.player.max_magic)), 15))
        
        magic_text = self.font_small.render(f"{int(self.player.magic)}/{self.player.max_magic}", True, WHITE)
        surface.blit(magic_text, (25, 42))
        
        # 绘制森林健康度
        # forest_health_text = self.font_small.render(f"森林健康度: {int(self.player.world.forest_health)}%", True, GREEN)
        # surface.blit(forest_health_text, (SCREEN_WIDTH//2 - 200, 20))
    
    def draw_skill_icons(self, surface):
        for i, icon in enumerate(self.skill_icons):
            # 绘制图标背景
            surface.blit(icon["surface"], icon["rect"])
            
            # 绘制冷却覆盖层
            if icon["cooldown"] > 0:
                cooldown_height = icon["rect"].height * (icon["cooldown"] / icon["max_cooldown"])
                cooldown_rect = pygame.Rect(
                    icon["rect"].x, 
                    icon["rect"].y + icon["rect"].height - cooldown_height,
                    icon["rect"].width,
                    cooldown_height
                )
                cooldown_surface = pygame.Surface((cooldown_rect.width, cooldown_rect.height))
                cooldown_surface.set_alpha(150)
                cooldown_surface.fill((50, 50, 50))
                surface.blit(cooldown_surface, cooldown_rect)
            
            # 绘制技能按键
            key_text = self.font_small.render(icon["key"], True, WHITE)
            surface.blit(key_text, (icon["rect"].x + 5, icon["rect"].y + 5))
            
            # 绘制技能消耗
            cost_text = self.font_small.render(str(icon["cost"]), True, WHITE)
            surface.blit(cost_text, (icon["rect"].x + icon["rect"].width - 20, 
                                   icon["rect"].y + icon["rect"].height - 20))
            
            # 标记无法使用的技能（魔法不足）
            if self.player.magic < icon["cost"]:
                cross_surface = pygame.Surface((icon["rect"].width, icon["rect"].height), pygame.SRCALPHA)
                pygame.draw.line(cross_surface, (255, 0, 0, 150), (0, 0), 
                               (icon["rect"].width, icon["rect"].height), 3)
                pygame.draw.line(cross_surface, (255, 0, 0, 150), 
                               (0, icon["rect"].height), (icon["rect"].width, 0), 3)
                surface.blit(cross_surface, icon["rect"])
    
    def draw_tooltip(self, surface):
        tooltip_text = self.skill_tooltips[self.active_tooltip]
        tooltip_surface = self.font_small.render(tooltip_text, True, WHITE)
        tooltip_rect = tooltip_surface.get_rect()
        tooltip_rect.bottomleft = (self.skill_icons[self.active_tooltip]["rect"].x, 
                                 self.skill_icons[self.active_tooltip]["rect"].y - 5)
        
        # 绘制背景
        bg_rect = tooltip_rect.inflate(10, 10)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surface, WHITE, bg_rect, 1)
        
        # 绘制文本
        surface.blit(tooltip_surface, tooltip_rect)
    
    def check_hover(self, pos):
        # 检查技能图标悬停
        for i, icon in enumerate(self.skill_icons):
            if icon["rect"].collidepoint(pos):
                self.show_tooltip(i)
                return True
        
        # 检查暂停按钮悬停
        return self.pause_button.check_hover(pos)
    
    def handle_click(self, pos, event):
        # 检查暂停按钮点击
        if self.pause_button.is_clicked(pos, event):
            return "pause"
        
        # 检查技能图标点击
        for i, icon in enumerate(self.skill_icons):
            if icon["rect"].collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN:
                if icon["cooldown"] == 0 and self.player.magic >= icon["cost"]:
                    return f"skill_{i+1}"
        
        return None

# 主菜单UI类
class MainMenuUI:
    def __init__(self):
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large
        self.title_font = title_font
        
        # 创建按钮
        button_width = 250
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.buttons = [
            Button(button_x, 250, button_width, button_height, "开始游戏", self.font_medium),
            Button(button_x, 330, button_width, button_height, "选择关卡", self.font_medium),
            Button(button_x, 410, button_width, button_height, "设置", self.font_medium),
            Button(button_x, 490, button_width, button_height, "退出", self.font_medium)
        ]
    
    def draw(self, surface):
        # 绘制标题
        title_text = self.title_font.render("森林守护者", True, GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 120))
        surface.blit(title_text, title_rect)
        
        # 绘制副标题
        subtitle_text = self.font_medium.render("守护自然，拯救森林", True, (0, 150, 0))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        surface.blit(subtitle_text, subtitle_rect)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)
        
        # 绘制版权信息
        copyright_text = self.font_small.render("© 2023 森林守护者团队", True, WHITE)
        copyright_rect = copyright_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        surface.blit(copyright_text, copyright_rect)


# 角色选择UI类
class CharacterSelectUI:
    def __init__(self):
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # 角色选择框
        self.lia_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 200, 200, 300)
        self.karn_rect = pygame.Rect(SCREEN_WIDTH // 2 + 50, 200, 200, 300)

        # 创建按钮
        self.back_button = Button(50, SCREEN_HEIGHT - 100, 150, 50, "返回", self.font_medium)

        # 角色信息
        self.lia_info = {
            "name": "莉娅 (Lia)",
            "type": "森林精灵",
            "skills": ["藤蔓缠绕", "治愈之触", "花朵陷阱"],
            "color": (0, 200, 100),
            "selected": False
        }

        self.karn_info = {
            "name": "卡恩 (Karn)",
            "type": "树人战士",
            "skills": ["大地震击", "树皮护甲", "根系束缚"],
            "color": (139, 69, 19),
            "selected": False
        }
        # 加载角色闲置帧图像
        self.character_scale = 8  # 角色图像缩放比例
        self.load_character_images()

    def load_character_images(self):
        """加载角色的闲置帧图像"""
        try:
            # 加载莉娅的闲置帧（帧索引0）
            self.lia_image = load_image("lia", self.character_scale, 0)

            # 加载卡恩的闲置帧（帧索引0）
            self.karn_image = load_image("karn", self.character_scale, 0)
        except Exception as e:
            print(f"加载角色图像时出错: {e}")
            # 如果加载失败，创建占位符图像
            self.lia_image = pygame.Surface((64, 64))
            self.lia_image.fill((0, 200, 100))  # 莉娅用绿色

            self.karn_image = pygame.Surface((64, 64))
            self.karn_image.fill((139, 69, 19))  # 卡恩用棕色

    def draw(self, surface):
        # 绘制标题
        title_text = self.font_large.render("选择你的角色", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)

        # 绘制莉娅选择框
        border_color = GREEN if self.lia_info["selected"] else WHITE
        pygame.draw.rect(surface, self.lia_info["color"], self.lia_rect)
        pygame.draw.rect(surface, border_color, self.lia_rect, 3)

        # 在莉娅选择框中心绘制角色图像
        lia_image_rect = self.lia_image.get_rect()
        lia_image_rect.center = (self.lia_rect.centerx, self.lia_rect.centery - 20)
        surface.blit(self.lia_image, lia_image_rect)

        # 绘制卡恩选择框
        border_color = GREEN if self.karn_info["selected"] else WHITE
        pygame.draw.rect(surface, self.karn_info["color"], self.karn_rect)
        pygame.draw.rect(surface, border_color, self.karn_rect, 3)

        # 在卡恩选择框中心绘制角色图像
        karn_image_rect = self.karn_image.get_rect()
        karn_image_rect.center = (self.karn_rect.centerx, self.karn_rect.centery - 20)
        surface.blit(self.karn_image, karn_image_rect)

        # 绘制角色名称
        lia_name = self.font_medium.render(self.lia_info["name"], True, WHITE)
        karn_name = self.font_medium.render(self.karn_info["name"], True, WHITE)

        surface.blit(lia_name, (self.lia_rect.centerx - lia_name.get_width() // 2,
                                self.lia_rect.y + self.lia_rect.height + 10))

        surface.blit(karn_name, (self.karn_rect.centerx - karn_name.get_width() // 2,
                                 self.karn_rect.y + self.karn_rect.height + 10))

        # 绘制角色类型
        lia_type = self.font_small.render(self.lia_info["type"], True, WHITE)
        karn_type = self.font_small.render(self.karn_info["type"], True, WHITE)

        surface.blit(lia_type, (self.lia_rect.centerx - lia_type.get_width() // 2,
                                self.lia_rect.y + self.lia_rect.height + 40))

        surface.blit(karn_type, (self.karn_rect.centerx - karn_type.get_width() // 2,
                                 self.karn_rect.y + self.karn_rect.height + 40))

        # 绘制角色技能
        for i, skill in enumerate(self.lia_info["skills"]):
            skill_text = self.font_small.render(f"· {skill}", True, WHITE)
            surface.blit(skill_text, (self.lia_rect.x + 10,
                                      self.lia_rect.y + self.lia_rect.height + 70 + i * 25))

        for i, skill in enumerate(self.karn_info["skills"]):
            skill_text = self.font_small.render(f"· {skill}", True, WHITE)
            surface.blit(skill_text, (self.karn_rect.x + 10,
                                      self.karn_rect.y + self.karn_rect.height + 70 + i * 25))

        # 绘制返回按钮
        self.back_button.draw(surface)

    def handle_event(self, event, mouse_pos):
        # 处理鼠标移动事件
        if event.type == pygame.MOUSEMOTION:
            # 检查返回按钮悬停
            self.back_button.check_hover(mouse_pos)

            # 检查角色选择框悬停
            self.lia_info["selected"] = self.lia_rect.collidepoint(mouse_pos)
            self.karn_info["selected"] = self.karn_rect.collidepoint(mouse_pos)

        # 处理鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查是否点击返回按钮
            if self.back_button.is_clicked(mouse_pos, event):
                return "back"

            # 检查是否点击角色选择框
            if self.lia_rect.collidepoint(mouse_pos):
                return "lia"

            if self.karn_rect.collidepoint(mouse_pos):
                return "karn"

        return None


# 暂停菜单UI类
class PauseMenuUI:
    def __init__(self):
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # 暂停菜单背景
        self.bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200, 400, 400)

        # 创建按钮
        button_width = 300
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        self.buttons = [
            Button(button_x, self.bg_rect.y + 100, button_width, button_height, "继续游戏", self.font_medium),
            Button(button_x, self.bg_rect.y + 170, button_width, button_height, "返回主菜单", self.font_medium),
            Button(button_x, self.bg_rect.y + 240, button_width, button_height, "退出游戏", self.font_medium)
        ]

    def draw(self, surface):
        # 绘制半透明背景
        bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))
        surface.blit(bg_surface, (0, 0))

        # 绘制暂停菜单背景
        pygame.draw.rect(surface, (50, 50, 50), self.bg_rect)
        pygame.draw.rect(surface, WHITE, self.bg_rect, 2)

        # 绘制标题
        title_text = self.font_large.render("游戏暂停", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.bg_rect.y + 50))
        surface.blit(title_text, title_rect)

        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event, mouse_pos):
        # 处理鼠标移动事件
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_hover(mouse_pos)

        # 处理鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons[0].is_clicked(mouse_pos, event):
                return "resume"
            elif self.buttons[1].is_clicked(mouse_pos, event):
                return "main_menu"
            elif self.buttons[2].is_clicked(mouse_pos, event):
                return "quit"

        return None


# 游戏结束UI类
class GameOverUI:
    def __init__(self):
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # 菜单背景
        self.bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400)

        # 创建按钮
        button_width = 300
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        self.buttons = [
            Button(button_x, self.bg_rect.y + 200, button_width, button_height, "重新尝试", self.font_medium),
            Button(button_x, self.bg_rect.y + 270, button_width, button_height, "返回主菜单", self.font_medium)
        ]

    def draw(self, surface):
        # 绘制半透明背景
        bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        surface.blit(bg_surface, (0, 0))

        # 绘制游戏结束菜单背景
        pygame.draw.rect(surface, (50, 0, 0), self.bg_rect)
        pygame.draw.rect(surface, (200, 0, 0), self.bg_rect, 2)

        # 绘制标题
        title_text = self.font_large.render("游戏结束", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.bg_rect.y + 70))
        surface.blit(title_text, title_rect)

        # 绘制提示文字
        hint_text = self.font_medium.render("森林已被摧毁，试着再来一次吧！", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, self.bg_rect.y + 140))
        surface.blit(hint_text, hint_rect)

        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event, mouse_pos):
        # 处理鼠标移动事件
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_hover(mouse_pos)

        # 处理鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons[0].is_clicked(mouse_pos, event):
                return "retry"
            elif self.buttons[1].is_clicked(mouse_pos, event):
                return "main_menu"

        return None


# 胜利UI类
class VictoryUI:
    def __init__(self):
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # 菜单背景
        self.bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 250, 600, 500)

        # 创建按钮
        button_width = 300
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        self.buttons = [
            Button(button_x, self.bg_rect.y + 400, button_width, button_height, "返回主菜单", self.font_medium)
        ]

    def draw(self, surface):
        # 绘制胜利背景图（这里简化为蓝绿色渐变背景）
        for i in range(SCREEN_HEIGHT):
            color_value = int(i / SCREEN_HEIGHT * 255)
            pygame.draw.line(surface, (0, color_value, 100), (0, i), (SCREEN_WIDTH, i))

        # 绘制标题
        title_text = self.font_large.render("胜利！", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)

        # 绘制副标题
        subtitle_text = self.font_medium.render("你成功守护了森林！", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        surface.blit(subtitle_text, subtitle_rect)

        # 绘制结局文字
        ending_texts = [
            "贪婪商人被击败，森林恢复了生机。",
            "在你的守护下，动植物重新繁荣起来。",
            "森林的精灵们歌颂着你的英勇事迹。",
            "你的名字将永远铭刻在世界之树上。",
            "感谢你成为真正的森林守护者！"
        ]

        for i, text in enumerate(ending_texts):
            text_surf = self.font_small.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 40))
            surface.blit(text_surf, text_rect)

        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event, mouse_pos):
        # 处理鼠标移动事件
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_hover(mouse_pos)

        # 处理鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons[0].is_clicked(mouse_pos, event):
                return "main_menu"

        return None


# 过场动画UI类
class CutsceneUI:
    def __init__(self, texts, next_state=GameState.PLAYING):
        # 字体
        self.font_small = font_small
        self.font_medium = font_medium

        # 文本内容和计时器
        self.texts = texts
        self.current_text_index = 0
        self.text_timer = 0
        self.text_duration = 300  # 每段文本显示5秒

        # 下一个游戏状态
        self.next_state = next_state

        # 跳过按钮
        self.skip_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 70, 120, 50, "跳过", self.font_medium)

    def draw(self, surface):
        # 绘制黑色背景
        surface.fill(BLACK)

        # 如果还有文本要显示
        if self.current_text_index < len(self.texts):
            # 绘制当前文本
            text = self.texts[self.current_text_index]
            text_lines = text.split('\n')

            for i, line in enumerate(text_lines):
                text_surf = self.font_medium.render(line, True, WHITE)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50 + i * 40))
                surface.blit(text_surf, text_rect)

            # 绘制提示
            hint_text = self.font_small.render("点击继续...", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            surface.blit(hint_text, hint_rect)

        # 绘制跳过按钮
        self.skip_button.draw(surface)

    def update(self):
        # 更新文本显示
        self.text_timer += 1
        if self.text_timer >= self.text_duration:
            self.text_timer = 0
            self.current_text_index += 1

    def handle_event(self, event, mouse_pos):
        # 处理鼠标移动
        if event.type == pygame.MOUSEMOTION:
            self.skip_button.check_hover(mouse_pos)

        # 处理鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查是否点击跳过按钮
            if self.skip_button.is_clicked(mouse_pos, event):
                return self.next_state

            # 点击任意位置继续显示下一段文本
            self.current_text_index += 1
            self.text_timer = 0

            # 如果所有文本都已显示完，进入下一个状态
            if self.current_text_index >= len(self.texts):
                return self.next_state

        return None


class TutorialUI:
    def __init__(self):
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small

        # 教程内容
        self.tutorial_pages = [
            {
                "title": "基础操作",
                "content": [
                    "A键 - 向左移动",
                    "D键 - 向右移动",
                    "空格键 - 跳跃",
                    "J键 - 普通攻击"
                ]
            },
            {
                "title": "技能操作",
                "content": [
                    "1键 - 使用技能1",
                    "2键 - 使用技能2",
                    "3键 - 使用技能3",
                    "技能需要消耗魔法值"
                ]
            },
            {
                "title": "游戏目标",
                "content": [
                    "消灭所有敌人完成关卡",
                    "保护森林生命值不归零",
                    "合理使用技能和普攻",
                    # "收集道具恢复生命和魔法"
                ]
            },
            {
                "title": "系统操作",
                "content": [
                    "ESC键 - 暂停游戏",
                    "F10键 - 开发者模式开关",
                    "鼠标点击UI按钮操作",
                    "准备好了就开始游戏吧！"
                ]
            }
        ]

        self.current_page = 0
        self.max_page = len(self.tutorial_pages) - 1

        # 创建按钮
        button_width = 120
        button_height = 40
        button_y = SCREEN_HEIGHT - 80

        self.prev_button = Button(50, button_y, button_width, button_height, "上一页", font_medium)
        self.next_button = Button(200, button_y, button_width, button_height, "下一页", font_medium)
        self.skip_button = Button(SCREEN_WIDTH - 170, button_y, button_width, button_height, "跳过", font_medium)
        self.start_button = Button(SCREEN_WIDTH // 2 - 60, button_y, button_width, button_height, "开始游戏",
                                   font_medium)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEMOTION:
            self.prev_button.check_hover(mouse_pos)
            self.next_button.check_hover(mouse_pos)
            self.skip_button.check_hover(mouse_pos)
            self.start_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.prev_button.is_clicked(mouse_pos, event) and self.current_page > 0:
                self.current_page -= 1
                return "prev"
            elif self.next_button.is_clicked(mouse_pos, event) and self.current_page < self.max_page:
                self.current_page += 1
                return "next"
            elif self.skip_button.is_clicked(mouse_pos, event):
                return "skip"
            elif self.start_button.is_clicked(mouse_pos, event) and self.current_page == self.max_page:
                return "start"

        # 键盘快捷键
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.current_page > 0:
                self.current_page -= 1
                return "prev"
            elif event.key == pygame.K_RIGHT and self.current_page < self.max_page:
                self.current_page += 1
                return "next"
            elif event.key == pygame.K_ESCAPE:
                return "skip"
            elif event.key == pygame.K_RETURN and self.current_page == self.max_page:
                return "start"

        return None

    def draw(self, screen):
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 绘制教程框
        tutorial_width = 600
        tutorial_height = 400
        tutorial_x = (SCREEN_WIDTH - tutorial_width) // 2
        tutorial_y = (SCREEN_HEIGHT - tutorial_height) // 2

        tutorial_rect = pygame.Rect(tutorial_x, tutorial_y, tutorial_width, tutorial_height)
        pygame.draw.rect(screen, (40, 40, 40), tutorial_rect)
        pygame.draw.rect(screen, (100, 100, 100), tutorial_rect, 3)

        # 绘制当前页内容
        current_tutorial = self.tutorial_pages[self.current_page]

        # 绘制标题
        title_text = self.font_large.render(current_tutorial["title"], True, (255, 255, 255))
        title_x = tutorial_x + (tutorial_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, tutorial_y + 30))

        # 绘制内容
        content_start_y = tutorial_y + 100
        for i, line in enumerate(current_tutorial["content"]):
            line_text = self.font_medium.render(line, True, (200, 200, 200))
            line_x = tutorial_x + 50
            line_y = content_start_y + i * 40
            screen.blit(line_text, (line_x, line_y))

        # 绘制页码指示器
        page_info = f"{self.current_page + 1}/{len(self.tutorial_pages)}"
        page_text = self.font_small.render(page_info, True, (150, 150, 150))
        page_x = tutorial_x + tutorial_width - page_text.get_width() - 20
        page_y = tutorial_y + tutorial_height - 40
        screen.blit(page_text, (page_x, page_y))

        # 绘制按钮
        if self.current_page > 0:
            self.prev_button.draw(screen)

        if self.current_page < self.max_page:
            self.next_button.draw(screen)

        self.skip_button.draw(screen)

        if self.current_page == self.max_page:
            self.start_button.draw(screen)

        # 绘制提示文本
        if self.current_page < self.max_page:
            hint_text = "使用左右箭头键或点击按钮翻页"
        else:
            hint_text = "按回车键或点击开始游戏按钮"

        hint_surface = self.font_small.render(hint_text, True, (150, 150, 150))
        hint_x = (SCREEN_WIDTH - hint_surface.get_width()) // 2
        hint_y = SCREEN_HEIGHT - 30
        screen.blit(hint_surface, (hint_x, hint_y))


class SettingsUI:
    def __init__(self):
        # 设置面板背景
        self.panel_width = 600
        self.panel_height = 500
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2

        # 创建设置面板背景
        self.panel = pygame.Surface((self.panel_width, self.panel_height))
        self.panel.fill((30, 30, 30))
        self.panel.set_alpha(220)

        # 边框
        self.border_color = (100, 100, 100)

        # 标题
        self.title_font = font_large
        self.option_font = font_medium
        self.value_font = font_small

        # 音量滑块设置
        self.slider_width = 200
        self.slider_height = 20
        self.slider_handle_width = 15
        self.slider_handle_height = 25

        # 音乐音量滑块
        self.music_slider_x = self.panel_x + 250
        self.music_slider_y = self.panel_y + 120
        self.music_volume = 0.7  # 默认值
        self.music_dragging = False

        # 音效音量滑块
        self.sound_slider_x = self.panel_x + 250
        self.sound_slider_y = self.panel_y + 180
        self.sound_volume = 0.8  # 默认值
        self.sound_dragging = False

        # 分辨率选项
        self.resolution_options = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1920, 1080)
        ]
        self.current_resolution_index = 2  # 默认1280x720

        # 全屏选项
        self.fullscreen = False

        # 按钮
        self.create_buttons()

    def create_buttons(self):
        """创建按钮"""
        button_width = 120
        button_height = 40
        button_spacing = 20

        # 分辨率切换按钮
        self.resolution_button = Button(
            self.panel_x + 250,
            self.panel_y + 240,
            button_width + 50,
            button_height,
            f"{self.resolution_options[self.current_resolution_index][0]}x{self.resolution_options[self.current_resolution_index][1]}",
            font_small
        )

        # 全屏切换按钮
        self.fullscreen_button = Button(
            self.panel_x + 250,
            self.panel_y + 300,
            button_width,
            button_height,
            "开启" if self.fullscreen else "关闭",
            font_small
        )

        # 应用设置按钮
        self.apply_button = Button(
            self.panel_x + 150,
            self.panel_y + 380,
            button_width,
            button_height,
            "应用",
            font_medium,
            (0, 150, 0)
        )

        # 重置按钮
        self.reset_button = Button(
            self.panel_x + 280,
            self.panel_y + 380,
            button_width,
            button_height,
            "重置",
            font_medium,
            (150, 150, 0)
        )

        # 返回按钮
        self.back_button = Button(
            self.panel_x + 410,
            self.panel_y + 380,
            button_width,
            button_height,
            "返回",
            font_medium,
            (150, 0, 0)
        )

        self.buttons = [
            self.resolution_button,
            self.fullscreen_button,
            self.apply_button,
            self.reset_button,
            self.back_button
        ]

    def handle_event(self, event, mouse_pos):
        """处理事件"""
        # 处理滑块拖拽
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 检查音乐音量滑块
                music_handle_x = self.music_slider_x + (self.music_volume * self.slider_width) - (
                            self.slider_handle_width // 2)
                music_handle_rect = pygame.Rect(music_handle_x, self.music_slider_y - 2, self.slider_handle_width,
                                                self.slider_handle_height)
                if music_handle_rect.collidepoint(mouse_pos):
                    self.music_dragging = True

                # 检查音效音量滑块
                sound_handle_x = self.sound_slider_x + (self.sound_volume * self.slider_width) - (
                            self.slider_handle_width // 2)
                sound_handle_rect = pygame.Rect(sound_handle_x, self.sound_slider_y - 2, self.slider_handle_width,
                                                self.slider_handle_height)
                if sound_handle_rect.collidepoint(mouse_pos):
                    self.sound_dragging = True

                # 检查是否点击滑块轨道
                music_track_rect = pygame.Rect(self.music_slider_x, self.music_slider_y, self.slider_width,
                                               self.slider_height)
                if music_track_rect.collidepoint(mouse_pos) and not self.music_dragging:
                    # 直接设置音乐音量到点击位置
                    relative_x = mouse_pos[0] - self.music_slider_x
                    self.music_volume = max(0.0, min(1.0, relative_x / self.slider_width))

                sound_track_rect = pygame.Rect(self.sound_slider_x, self.sound_slider_y, self.slider_width,
                                               self.slider_height)
                if sound_track_rect.collidepoint(mouse_pos) and not self.sound_dragging:
                    # 直接设置音效音量到点击位置
                    relative_x = mouse_pos[0] - self.sound_slider_x
                    self.sound_volume = max(0.0, min(1.0, relative_x / self.slider_width))

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.music_dragging = False
                self.sound_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            # 拖拽滑块
            if self.music_dragging:
                relative_x = mouse_pos[0] - self.music_slider_x
                self.music_volume = max(0.0, min(1.0, relative_x / self.slider_width))

            if self.sound_dragging:
                relative_x = mouse_pos[0] - self.sound_slider_x
                self.sound_volume = max(0.0, min(1.0, relative_x / self.slider_width))

            # 检查按钮悬停
            for button in self.buttons:
                button.check_hover(mouse_pos)

        # 处理按钮点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.resolution_button.is_clicked(mouse_pos, event):
                self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolution_options)
                self.resolution_button.text = f"{self.resolution_options[self.current_resolution_index][0]}x{self.resolution_options[self.current_resolution_index][1]}"
                return "resolution_change"

            elif self.fullscreen_button.is_clicked(mouse_pos, event):
                self.fullscreen = not self.fullscreen
                self.fullscreen_button.text = "开启" if self.fullscreen else "关闭"
                return "fullscreen_toggle"

            elif self.apply_button.is_clicked(mouse_pos, event):
                return "apply"

            elif self.reset_button.is_clicked(mouse_pos, event):
                return "reset"

            elif self.back_button.is_clicked(mouse_pos, event):
                return "back"

        return None

    def reset_settings(self):
        """重置设置到默认值"""
        self.music_volume = 0.7
        self.sound_volume = 0.8
        self.current_resolution_index = 2
        self.fullscreen = False
        self.fullscreen_button.text = "关闭"
        self.resolution_button.text = f"{self.resolution_options[self.current_resolution_index][0]}x{self.resolution_options[self.current_resolution_index][1]}"

    def get_current_resolution(self):
        """获取当前选择的分辨率"""
        return self.resolution_options[self.current_resolution_index]

    def draw_slider(self, screen, x, y, value, label):
        """绘制滑块"""
        # 绘制标签
        label_text = self.option_font.render(label, True, (255, 255, 255))
        screen.blit(label_text, (x - 200, y - 2))

        # 绘制滑块轨道
        track_rect = pygame.Rect(x, y, self.slider_width, self.slider_height)
        pygame.draw.rect(screen, (100, 100, 100), track_rect)
        pygame.draw.rect(screen, (200, 200, 200), track_rect, 2)

        # 绘制已填充部分
        filled_width = int(value * self.slider_width)
        if filled_width > 0:
            filled_rect = pygame.Rect(x, y, filled_width, self.slider_height)
            pygame.draw.rect(screen, (0, 150, 255), filled_rect)

        # 绘制滑块手柄
        handle_x = x + (value * self.slider_width) - (self.slider_handle_width // 2)
        handle_y = y - 2
        handle_rect = pygame.Rect(handle_x, handle_y, self.slider_handle_width, self.slider_handle_height)
        pygame.draw.rect(screen, (255, 255, 255), handle_rect)
        pygame.draw.rect(screen, (150, 150, 150), handle_rect, 2)

        # 绘制音量百分比
        percentage = int(value * 100)
        percentage_text = self.value_font.render(f"{percentage}%", True, (255, 255, 255))
        screen.blit(percentage_text, (x + self.slider_width + 20, y + 2))

    def draw(self, screen):
        """绘制设置界面"""
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        screen.blit(overlay, (0, 0))

        # 绘制设置面板
        screen.blit(self.panel, (self.panel_x, self.panel_y))
        pygame.draw.rect(screen, self.border_color,
                         (self.panel_x, self.panel_y, self.panel_width, self.panel_height), 3)

        # 绘制标题
        title_text = self.title_font.render("游戏设置", True, (255, 255, 255))
        title_x = self.panel_x + (self.panel_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, self.panel_y + 20))

        # 绘制音频设置标题
        audio_title = self.option_font.render("音频设置", True, (200, 200, 200))
        screen.blit(audio_title, (self.panel_x + 50, self.panel_y + 80))

        # 绘制音乐音量滑块
        self.draw_slider(screen, self.music_slider_x, self.music_slider_y, self.music_volume, "音乐音量:")

        # 绘制音效音量滑块
        self.draw_slider(screen, self.sound_slider_x, self.sound_slider_y, self.sound_volume, "音效音量:")

        # 绘制显示设置标题
        display_title = self.option_font.render("显示设置", True, (200, 200, 200))
        screen.blit(display_title, (self.panel_x + 50, self.panel_y + 220))

        # 绘制分辨率选项
        resolution_label = self.option_font.render("分辨率:", True, (255, 255, 255))
        screen.blit(resolution_label, (self.panel_x + 50, self.panel_y + 250))

        # 绘制全屏选项
        fullscreen_label = self.option_font.render("全屏模式:", True, (255, 255, 255))
        screen.blit(fullscreen_label, (self.panel_x + 50, self.panel_y + 310))

        # 绘制所有按钮
        for button in self.buttons:
            button.draw(screen)

        # 绘制提示信息
        hint_text = self.value_font.render("提示: 点击应用按钮保存设置", True, (180, 180, 180))
        hint_x = self.panel_x + (self.panel_width - hint_text.get_width()) // 2
        screen.blit(hint_text, (hint_x, self.panel_y + 450))


class LevelSelectUI:
    def __init__(self):
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # 创建关卡按钮
        self.level_buttons = []
        self.max_level = 9  # 总关卡数

        # 创建关卡按钮网格 (3x3)
        button_width = 100
        button_height = 80
        cols = 3
        rows = 3

        start_x = (SCREEN_WIDTH - (cols * button_width + (cols - 1) * 20)) // 2
        start_y = 200

        for i in range(self.max_level):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_width + 20)
            y = start_y + row * (button_height + 30)

            level_button = Button(x, y, button_width, button_height,
                                  f"关卡 {i + 1}", self.font_medium)
            self.level_buttons.append(level_button)

        # 返回按钮
        self.back_button = Button(50, SCREEN_HEIGHT - 80, 100, 50,
                                  "返回", self.font_medium)


    def handle_event(self, event, mouse_pos):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            # 关卡选择界面
            for button in self.level_buttons:
                button.check_hover(mouse_pos)
            self.back_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 关卡选择界面
            for i, button in enumerate(self.level_buttons):
                if button.is_clicked(mouse_pos, event):
                    self.selected_level = i + 1
                    return {"level": self.selected_level}

            if self.back_button.is_clicked(mouse_pos, event):
                return "back"

        return None

    def draw(self, screen):
        """绘制界面"""
        # 绘制关卡选择界面
        title_text = self.font_large.render("选择关卡", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # 绘制关卡按钮
        for button in self.level_buttons:
            button.draw(screen)

        # 绘制返回按钮
        self.back_button.draw(screen)

        # 绘制提示文字
        hint_text = self.font_small.render("点击关卡进入角色选择", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(hint_text, hint_rect)