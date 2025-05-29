import math

import pygame
import random
import os
from constants import *


class World:
    def __init__(self, level, level_data=None):
        self.tile_size = TILE_SIZE
        self.tile_list = []
        self.forest_health = 100  # 森林健康度
        self.level = level
        self.max_level_health = 100

        # 加载图像
        self.dirt_img = pygame.Surface((self.tile_size, self.tile_size))
        self.dirt_img.fill(DARK_BROWN)  # 棕色表示泥土

        self.grass_img = pygame.Surface((self.tile_size, self.tile_size))
        self.grass_img.fill(LIGHT_GREEN)  # 绿色表示草地

        self.water_img = pygame.Surface((self.tile_size, self.tile_size))
        self.water_img.fill(BLUE)  # 蓝色表示水

        self.tree_img = pygame.Surface((self.tile_size * 2, self.tile_size * 3))
        self.tree_img.fill(GREEN)  # 绿色表示树

        self.pollution_img = pygame.Surface((self.tile_size, self.tile_size))
        self.pollution_img.fill(PURPLE)  # 紫色表示污染

        # 定义每个关卡的环境特征
        self.level_names = {
            1: "晨雾之林",  # 第一章：苏醒的森林 - 区域1
            2: "溪流峡谷",  # 第一章：苏醒的森林 - 区域2
            3: "初次遭遇",  # 第一章：苏醒的森林 - 区域3
            4: "雾霭沼泽",  # 第二章：蔓延的污染 - 区域1
            5: "枯萎森林",  # 第二章：蔓延的污染 - 区域2
            6: "工厂前哨",  # 第二章：蔓延的污染 - 区域3
            7: "古树谷地",  # 第三章：最后的守护 - 区域1
            8: "伐木营地",  # 第三章：最后的守护 - 区域2
            9: "世界之树"  # 第三章：最后的守护 - 区域3
        }

        # 加载关卡数据
        self.load_level(level)

        # 收集物列表
        self.collectibles = []

        # 环境特效（例如漂浮的叶子、阳光光束等）
        self.environment_effects = []

        # 初始化环境特效
        self.initialize_environment_effects()

        # 创建树木和可收集物
        self.create_decorations()

    def tile_collide(self, x, y, width, height):
        # 检查是否与任何瓦片碰撞
        rect = pygame.Rect(x, y, width, height)
        for tile in self.tile_list:
            if tile[1].colliderect(rect):
                # 检查是否是特殊类型的瓦片
                if len(tile) > 2:
                    if tile[2] == "water":
                        return "water"
                    elif tile[2] == "pollution":
                        return "pollution"
                return True
        return False

    def load_level(self, level):
        self.tile_list = []

        # 根据关卡加载不同的地图数据
        if level == 1:
            data = self.generate_level_1()  # 晨雾之林
        elif level == 2:
            data = self.generate_level_2()  # 溪流峡谷
        elif level == 3:
            data = self.generate_level_3()  # 初次遭遇
        elif level == 4:
            data = self.generate_level_4()  # 雾霭沼泽
        elif level == 5:
            data = self.generate_level_5()  # 枯萎森林
        elif level == 6:
            data = self.generate_level_6()  # 工厂前哨
        elif level == 7:
            data = self.generate_level_7()  # 古树谷地
        elif level == 8:
            data = self.generate_level_8()  # 伐木营地
        elif level == 9:
            data = self.generate_level_9()  # 世界之树
        else:
            data = self.generate_default_level()  # 默认地图
        # 定义世界大小
        self.world_width = len(data[0]) * TILE_SIZE
        self.world_height = len(data) * TILE_SIZE

        # 创建地图
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:  # 泥土
                    img = self.dirt_img
                    img_rect = img.get_rect()
                    img_rect.x = col_count * self.tile_size
                    img_rect.y = row_count * self.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 2:  # 草地
                    img = self.grass_img
                    img_rect = img.get_rect()
                    img_rect.x = col_count * self.tile_size
                    img_rect.y = row_count * self.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:  # 水
                    img = self.water_img
                    img_rect = img.get_rect()
                    img_rect.x = col_count * self.tile_size
                    img_rect.y = row_count * self.tile_size
                    tile = (img, img_rect, "water")  # 标记为水
                    self.tile_list.append(tile)
                elif tile == 4:  # 污染
                    img = self.pollution_img
                    img_rect = img.get_rect()
                    img_rect.x = col_count * self.tile_size
                    img_rect.y = row_count * self.tile_size
                    tile = (img, img_rect, "pollution")  # 标记为污染
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def generate_default_level(self):
        # 创建默认关卡（平坦的地面，带有一些变化）
        level_width = SCREEN_WIDTH // self.tile_size * 2
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置地面
        for x in range(level_width):
            # 最底部两行都是泥土
            data[level_height - 1][x] = 1
            data[level_height - 2][x] = 1

            # 最上面一层是草地
            if x % 8 != 0:  # 留一些间隙作为坑
                data[level_height - 3][x] = 2

        # 添加一些平台
        for _ in range(10):
            platform_x = random.randint(0, level_width - 5)
            platform_y = random.randint(5, level_height - 8)
            platform_length = random.randint(3, 8)

            for i in range(platform_length):
                if platform_x + i < level_width:
                    data[platform_y][platform_x + i] = 2

        # 添加一些水和污染
        for _ in range(5):
            water_x = random.randint(10, level_width - 5)
            data[level_height - 3][water_x] = 3  # 水坑

            pollution_x = random.randint(10, level_width - 5)
            data[level_height - 3][pollution_x] = 4  # 污染

        return data

    def generate_level_1(self):
        # 晨雾之林 - 教学关卡，学习基本操作
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 地面为泥土
            data[level_height - 1][x] = 1
            data[level_height - 2][x] = 1

            # 草地表层，创建平坦的开始区域
            if x < 15 or (x > 20 and x < 50) or x > 60:
                data[level_height - 3][x] = 2

        # 添加一些简单的跳跃平台
        platforms = [
            (15, level_height - 6, 5),  # (x, y, 长度)
            (25, level_height - 8, 4),
            (35, level_height - 10, 3),
            (45, level_height - 7, 6),
            (55, level_height - 9, 4)
        ]

        for x, y, length in platforms:
            for i in range(length):
                data[y][x + i] = 2

        # 添加少量水潭作为障碍
        water_spots = [10, 20, 53]
        for x in water_spots:
            data[level_height - 3][x] = 3

        return data

    def generate_level_2(self):
        # 溪流峡谷 - 介绍水元素互动机制
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 地面为泥土
            data[level_height - 1][x] = 1

            # 创建起伏的地形，模拟峡谷
            if x < 10 or (x > 25 and x < 35) or (x > 50 and x < 60) or x > 70:
                data[level_height - 2][x] = 1
                data[level_height - 3][x] = 2

        # 添加溪流和水潭
        for x in range(10, 25):
            data[level_height - 2][x] = 3  # 溪流部分

        for x in range(35, 50):
            data[level_height - 2][x] = 3  # 溪流部分

        for x in range(60, 70):
            data[level_height - 2][x] = 3  # 溪流部分

        # 添加一些水上平台和踏脚石
        water_platforms = [
            (12, level_height - 3, 2),
            (17, level_height - 3, 2),
            (22, level_height - 3, 2),
            (37, level_height - 3, 2),
            (42, level_height - 3, 2),
            (47, level_height - 3, 2),
            (62, level_height - 3, 2),
            (67, level_height - 3, 2)
        ]

        for x, y, length in water_platforms:
            for i in range(length):
                data[y][x + i] = 2

        # 添加一些高地平台
        high_platforms = [
            (15, level_height - 6, 4),
            (30, level_height - 7, 5),
            (55, level_height - 8, 6),
            (68, level_height - 6, 5)
        ]

        for x, y, length in high_platforms:
            for i in range(length):
                data[y][min(x + i, len(data[y])-1)] = 2

        return data

    def generate_level_3(self):
        # 初次遭遇 - 首次与伐木工战斗
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 底部为泥土
            data[level_height - 1][x] = 1
            data[level_height - 2][x] = 1

            # 草地表层，创建开阔的战斗场地
            data[level_height - 3][x] = 2

        # 添加一些掩体和高地
        platforms = [
            (10, level_height - 6, 3),
            (20, level_height - 5, 4),
            (35, level_height - 7, 5),
            (50, level_height - 6, 3),
            (65, level_height - 8, 4)
        ]

        for x, y, length in platforms:
            for i in range(length):
                data[y][x + i] = 2

        # 添加一些被砍伐的树桩区域（用污染标记表示）
        stumps = [15, 25, 40, 55, 70]
        for x in stumps:
            data[level_height - 4][x] = 4

        return data

    def generate_level_4(self):
        # 雾霭沼泽 - 有毒气体区域，需要净化
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形 - 沼泽地形
        for x in range(level_width):
            data[level_height - 1][x] = 1  # 底层为泥土

            # 创建一些沼泽水域
            if (10 <= x <= 20) or (30 <= x <= 45) or (55 <= x <= 70):
                data[level_height - 2][x] = 3  # 水域
            else:
                data[level_height - 2][x] = 1  # 泥土
                if x % 3 != 0:  # 一些地方有草，但不是连续的
                    data[level_height - 3][x] = 2

        # 大量污染区域
        pollution_areas = [
            (5, level_height - 4, 8),
            (18, level_height - 3, 5),
            (35, level_height - 3, 10),
            (50, level_height - 4, 7),
            (65, level_height - 3, 8)
        ]

        for x, y, length in pollution_areas:
            for i in range(length):
                if 0 <= x + i < level_width and data[y][x + i] == 0:  # 确保不覆盖已有的地形
                    data[y][x + i] = 4  # 污染

        # 添加一些浮动平台
        platforms = [
            (12, level_height - 4, 2),
            (22, level_height - 5, 3),
            (32, level_height - 4, 2),
            (42, level_height - 6, 3),
            (60, level_height - 5, 4),
            (75, level_height - 7, 3)
        ]

        for x, y, length in platforms:
            for i in range(length):
                if 0 <= x + i < level_width:
                    data[y][x + i] = 2

        return data

    def generate_level_5(self):
        # 枯萎森林 - 救援被困的森林生物
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 底部为泥土
            data[level_height - 1][x] = 1

            # 大部分地面都是污染的
            if x % 4 == 0:
                data[level_height - 2][x] = 1  # 有些地方还是泥土
            else:
                data[level_height - 2][x] = 4  # 污染的地面

            # 部分地方有草，但很少
            if x % 10 == 0:
                data[level_height - 3][x] = 2

        # 添加枯萎的树平台（使用污染块表示）
        dead_trees = [
            (8, level_height - 8, 2),
            (18, level_height - 6, 2),
            (28, level_height - 7, 2),
            (38, level_height - 5, 2),
            (48, level_height - 9, 2),
            (58, level_height - 6, 2),
            (68, level_height - 8, 2)
        ]

        for x, y, length in dead_trees:
            for i in range(length):
                data[y][x + i] = 4  # 污染的平台
                data[y + 1][x + i] = 4  # 污染的平台延伸
                data[y + 2][x + i] = 4  # 污染的平台延伸

        # 添加一些健康的平台（草地）
        platforms = [
            (15, level_height - 4, 3),
            (25, level_height - 6, 3),
            (35, level_height - 8, 3),
            (45, level_height - 5, 3),
            (55, level_height - 7, 3),
            (65, level_height - 9, 3)
        ]

        for x, y, length in platforms:
            for i in range(length):
                data[y][x + i] = 2

        return data

    def generate_level_6(self):
        # 工厂前哨 - 摧毁污染源
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 底部为泥土
            data[level_height - 1][x] = 1

            # 地面全是污染
            data[level_height - 2][x] = 4

            # 部分区域添加工厂结构（用污染块表示）
            if 40 <= x <= 60:
                for y in range(level_height - 10, level_height - 2):
                    if (y == level_height - 10 or y == level_height - 6) and (x - 40) % 5 == 0:
                        data[y][x] = 4  # 污染源
                    elif y == level_height - 8 and 45 <= x <= 55:
                        data[y][x] = 4  # 污染平台

        # 添加一些机械平台(用污染块表示)
        mech_platforms = [
            (10, level_height - 5, 5),
            (20, level_height - 7, 5),
            (30, level_height - 4, 3),
            (65, level_height - 6, 4),
            (75, level_height - 8, 6)
        ]

        for x, y, length in mech_platforms:
            for i in range(length):
                if 0 <= x + i < level_width:
                    data[y][x + i] = 4

        # 添加一些废水水潭
        water_spots = [5, 15, 25, 70, 80]
        for x in water_spots:
            if 0 <= x < level_width:
                data[level_height - 3][x] = 3

        return data

    def generate_level_7(self):
        # 古树谷地 - 高难度平台跳跃
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形 - 不连续的地面，需要大量跳跃
        for x in range(level_width):
            # 最底层是泥土，但有很多间隙
            if x % 8 < 5:
                data[level_height - 1][x] = 1

            # 一些地方有水，增加难度
            if x % 16 == 0:
                data[level_height - 2][x] = 3
                data[level_height - 2][x + 1] = 3

        # 添加多层次的平台，形成复杂的跳跃路径
        platforms = [
            (8, level_height - 4, 2),
            (15, level_height - 6, 2),
            (22, level_height - 8, 2),
            (28, level_height - 10, 2),
            (35, level_height - 8, 2),
            (42, level_height - 6, 2),
            (48, level_height - 8, 2),
            (55, level_height - 10, 2),
            (62, level_height - 12, 2),
            (70, level_height - 10, 2),
            (76, level_height - 8, 2)
        ]

        for x, y, length in platforms:
            for i in range(length):
                if 0 <= x + i < level_width:
                    data[y][x + i] = 2

        # 添加一些移动困难的区域（用污染表示，实际游戏中可以是移动速度较慢的区域）
        difficult_areas = [
            (10, level_height - 3, 2),
            (30, level_height - 9, 2),
            (50, level_height - 7, 2),
            (65, level_height - 11, 2)
        ]

        for x, y, length in difficult_areas:
            for i in range(length):
                if 0 <= x + i < level_width and data[y][x + i] == 0:
                    data[y][x + i] = 4

        return data

    def generate_level_8(self):
        # 伐木营地 - 潜入敌人大本营
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 底层为泥土
            data[level_height - 1][x] = 1
            if x % 3 != 0:  # 一些地方有草
                data[level_height - 2][x] = 2

        # 创建伐木营地的结构
        # 主要建筑
        for x in range(30, 60):
            # 建筑底部
            data[level_height - 3][x] = 1
            data[level_height - 4][x] = 1

            # 建筑高度变化
        if 35 <= x <= 55:
            data[level_height - 5][x] = 1
            data[level_height - 6][x] = 1

            # 建筑顶部
            if 40 <= x <= 50:
                data[level_height - 7][x] = 1
                data[level_height - 8][x] = 1

            # 添加污染源（代表伐木机械和污染设备）
        pollution_spots = [
            (33, level_height - 7, 3),
            (42, level_height - 9, 5),
            (53, level_height - 7, 4),
            (65, level_height - 3, 6),
            (75, level_height - 3, 5)
        ]

        for x, y, length in pollution_spots:
            for i in range(length):
                if 0 <= x + i < level_width and data[y][x + i] == 0:
                    data[y][x + i] = 4

        # 添加一些战略位置的平台
        platforms = [
            (15, level_height - 5, 3),
            (25, level_height - 6, 2),
            (62, level_height - 6, 3),
            (70, level_height - 7, 2),
            (80, level_height - 5, 3)
        ]

        for x, y, length in platforms:
            for i in range(length):
                if 0 <= x + i < level_width:
                    data[y][x + i] = 2

        return data

    def generate_level_9(self):
        # 世界之树 - 保护森林的心脏
        level_width = SCREEN_WIDTH // self.tile_size * 3
        level_height = SCREEN_HEIGHT // self.tile_size

        data = [[0 for _ in range(level_width)] for _ in range(level_height)]

        # 设置基本地形
        for x in range(level_width):
            # 底部为泥土
            data[level_height - 1][x] = 1

            # 大部分地面是草地
            if x < 30 or x > 50:
                data[level_height - 2][x] = 2
            else:
                # 中央是世界之树的根部
                data[level_height - 2][x] = 1

        # 创建世界之树的结构（中央高耸的结构）
        tree_center = level_width // 2
        tree_width = 20

        # 树干底部
        for x in range(tree_center - tree_width // 2, tree_center + tree_width // 2):
            for y in range(level_height - 12, level_height - 2):
                # 树干中心
                if tree_center - 3 <= x <= tree_center + 3:
                    data[y][x] = 1  # 树干
                # 树枝
                elif y % 3 == 0 and abs(x - tree_center) <= (level_height - y) // 2:
                    data[y][x] = 2  # 树枝平台

        # 添加一些污染源（最终Boss战区域）
        pollution_spots = [
            (tree_center - 10, level_height - 3, 4),
            (tree_center + 6, level_height - 3, 4),
            (tree_center - 15, level_height - 5, 3),
            (tree_center + 12, level_height - 5, 3)
        ]

        for x, y, length in pollution_spots:
            for i in range(length):
                if 0 <= x + i < level_width and data[y][x + i] == 0:
                    data[y][x + i] = 4

        # 添加攀爬平台
        platforms = [
            (10, level_height - 4, 3),
            (20, level_height - 6, 3),
            (30, level_height - 8, 2),
            (50, level_height - 8, 2),
            (60, level_height - 6, 3),
            (70, level_height - 4, 3)
        ]

        for x, y, length in platforms:
            for i in range(length):
                if 0 <= x + i < level_width and data[y][x + i] == 0:
                    data[y][x + i] = 2

        return data

    def draw(self, surface, scroll):
        # 绘制瓦片
        for tile in self.tile_list:
            surface.blit(tile[0], (tile[1].x - scroll[0], tile[1].y - scroll[1]))

        # 绘制环境特效
        for effect in self.environment_effects:
            effect.draw(surface, scroll)

        # 绘制可收集物
        # for item in self.collectibles:
        #     if not item.get('collected', False):
        #         if item['type'] == 'magic':
        #             color = BLUE
        #         else:  # seed
        #             color = GREEN
        #
        #         pygame.draw.circle(
        #             surface,
        #             color,
        #             (item['x'] - scroll[0], item['y'] - scroll[1] + item['bob_offset']),
        #             10)
        #         # 绘制发光效果
        #         glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        #         pygame.draw.circle(glow_surf, (*color[:3], 100), (15, 15), 15)
        #         surface.blit(glow_surf, (item['x'] - scroll[0] - 15, item['y'] - scroll[1] + item['bob_offset'] - 15))
        self.draw_forest_health(surface)

    def draw_forest_health(self, surface):
        # 绘制森林健康度条
        bar_width = 200
        bar_height = 20
        x = SCREEN_WIDTH // 2 - bar_width - 20
        y = 20

        pygame.draw.rect(surface, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (x, y, int(bar_width * (self.forest_health / 100)), bar_height))

        text_surface = font_small.render(f"森林健康: {int(self.forest_health)}%", True, WHITE)
        surface.blit(text_surface, (x + 10, y + bar_height // 2 - text_surface.get_height() // 2))

    def check_collectible_collision(self, player_rect):
        for item in self.collectibles:
            if not item['collected']:
                item_rect = pygame.Rect(item['x'] - 10, item['y'] - 10 + item['bob_offset'], 20, 20)
                if player_rect.colliderect(item_rect):
                    item['collected'] = True
                    return item['type']
        return None


    def update(self):
        # 更新环境特效
        for effect in self.environment_effects:
            effect.update()

        # 过滤掉已经完成的特效
        self.environment_effects = [effect for effect in self.environment_effects if not effect.is_done]

    def create_decorations(self):
        # 根据关卡创建不同的装饰物（树木、花朵、蘑菇等）
        if self.level == 1:  # 晨雾之林
            self.create_fog_effects()
            self.create_trees(density=0.05)
            self.create_flowers(density=0.03)
        elif self.level == 2:  # 溪流峡谷
            self.create_water_effects()
            self.create_rocks(density=0.04)
        elif self.level == 3:  # 初次遭遇
            self.create_trees(density=0.03)
            self.create_stumps(density=0.02)
        elif self.level == 4:  # 雾霭沼泽
            self.create_fog_effects()
            self.create_pollution_effects()
            self.create_swamp_plants(density=0.04)
        elif self.level == 5:  # 枯萎森林
            self.create_dead_trees(density=0.05)
            self.create_pollution_effects()
        elif self.level == 6:  # 工厂前哨
            self.create_pollution_effects()
            self.create_machinery(density=0.03)
        elif self.level == 7:  # 古树谷地
            self.create_trees(density=0.06, large=True)
            self.create_flowers(density=0.04)
        elif self.level == 8:  # 伐木营地
            self.create_stumps(density=0.05)
            self.create_machinery(density=0.04)
        elif self.level == 9:  # 世界之树
            self.create_light_beams()
            self.create_flowers(density=0.06)
            self.create_magic_particles()

    def create_trees(self, density=0.04, large=False):
        # 在适当的地块上随机创建树木装饰
        for tile in self.tile_list:
            if len(tile) >= 3:
                continue  # 跳过水和污染等特殊地块

            if tile[1].y == SCREEN_HEIGHT - 3 * self.tile_size and random.random() < density:
                # 创建树
                tree_size = (2, 3) if not large else (3, 5)  # (宽度, 高度) 单位为tile_size
                tree = {
                    'img': pygame.Surface((tree_size[0] * self.tile_size, tree_size[1] * self.tile_size)),
                    'rect': pygame.Rect(tile[1].x, tile[1].y - tree_size[1] * self.tile_size,
                                        tree_size[0] * self.tile_size, tree_size[1] * self.tile_size),
                    'type': 'tree'
                }
                tree['img'].fill(GREEN)  # 简单的绿色表示树
                self.collectibles.append(tree)

    def create_flowers(self, density=0.03):
        # 创建花朵装饰
        for tile in self.tile_list:
            if len(tile) >= 3:
                continue  # 跳过水和污染等特殊地块

            if (tile[0] == self.grass_img and random.random() < density):
                # 创建花
                flower_size = self.tile_size // 2
                flower = {
                    'img': pygame.Surface((flower_size, flower_size)),
                    'rect': pygame.Rect(tile[1].x + random.randint(0, self.tile_size - flower_size),
                                        tile[1].y - flower_size, flower_size, flower_size),
                    'type': 'flower'
                }
                flower['img'].fill(random.choice([YELLOW, PINK, LIGHT_BLUE]))  # 随机花色
                self.collectibles.append(flower)

    def create_rocks(self, density=0.04):
        # 创建岩石装饰
        for tile in self.tile_list:
            if len(tile) >= 3:
                continue  # 跳过水和污染等特殊地块

            if random.random() < density:
                # 创建岩石
                rock_size = random.randint(self.tile_size // 3, self.tile_size // 2)
                rock = {
                    'img': pygame.Surface((rock_size, rock_size)),
                    'rect': pygame.Rect(tile[1].x + random.randint(0, self.tile_size - rock_size),
                                        tile[1].y - rock_size, rock_size, rock_size),
                    'type': 'rock'
                }
                rock['img'].fill(GRAY)  # 灰色表示岩石
                self.collectibles.append(rock)

    def create_stumps(self, density=0.02):
        # 创建树桩（被砍伐的树）
        for tile in self.tile_list:
            if len(tile) >= 3:
                continue  # 跳过水和污染等特殊地块

            if tile[1].y == SCREEN_HEIGHT - 3 * self.tile_size and random.random() < density:
                # 创建树桩
                stump_size = (self.tile_size, self.tile_size // 2)
                stump = {
                    'img': pygame.Surface(stump_size),
                    'rect': pygame.Rect(tile[1].x, tile[1].y - stump_size[1],
                                        stump_size[0], stump_size[1]),
                    'type': 'stump'
                }
                stump['img'].fill(BROWN)  # 棕色表示树桩
                self.collectibles.append(stump)

    def create_swamp_plants(self, density=0.04):
        # 创建沼泽植物
        for tile in self.tile_list:
            if len(tile) >= 3 and tile[2] == "water" and random.random() < density:
                # 创建沼泽植物
                plant_size = (self.tile_size // 2, self.tile_size)
                plant = {
                    'img': pygame.Surface(plant_size),
                    'rect': pygame.Rect(tile[1].x + random.randint(0, self.tile_size - plant_size[0]),
                                        tile[1].y - plant_size[1], plant_size[0], plant_size[1]),
                    'type': 'swamp_plant'
                }
                plant['img'].fill(DARK_GREEN)  # 深绿色表示沼泽植物
                self.collectibles.append(plant)

    def create_dead_trees(self, density=0.05):
        # 创建枯树
        for tile in self.tile_list:
            if len(tile) >= 3:
                continue  # 跳过水和污染等特殊地块

            if tile[1].y == SCREEN_HEIGHT - 3 * self.tile_size and random.random() < density:
                # 创建枯树
                tree_size = (2, 3)  # (宽度, 高度) 单位为tile_size
                tree = {
                    'img': pygame.Surface((tree_size[0] * self.tile_size, tree_size[1] * self.tile_size)),
                    'rect': pygame.Rect(tile[1].x, tile[1].y - tree_size[1] * self.tile_size,
                                        tree_size[0] * self.tile_size, tree_size[1] * self.tile_size),
                    'type': 'dead_tree'
                }
                tree['img'].fill(DARK_BROWN)  # 深棕色表示枯树
                self.collectibles.append(tree)

    def create_machinery(self, density=0.03):
        # 创建机械设备（伐木机等）
        for tile in self.tile_list:
            if len(tile) >= 3:
                continue  # 跳过水和污染等特殊地块

            if tile[1].y == SCREEN_HEIGHT - 3 * self.tile_size and random.random() < density:
                # 创建机械
                machine_size = (2, 2)  # (宽度, 高度) 单位为tile_size
                machine = {
                    'img': pygame.Surface((machine_size[0] * self.tile_size, machine_size[1] * self.tile_size)),
                    'rect': pygame.Rect(tile[1].x, tile[1].y - machine_size[1] * self.tile_size,
                                        machine_size[0] * self.tile_size, machine_size[1] * self.tile_size),
                    'type': 'machine'
                }
                machine['img'].fill(DARK_GRAY)  # 深灰色表示机械
                self.collectibles.append(machine)

    def initialize_environment_effects(self):
        # 根据关卡初始化相应的环境特效
        if self.level == 1:  # 晨雾之林
            self.create_fog_effects()
        elif self.level == 2:  # 溪流峡谷
            self.create_water_effects()
        elif self.level == 4:  # 雾霭沼泽
            self.create_fog_effects()
            self.create_pollution_effects()
        elif self.level == 5 or self.level == 6:  # 枯萎森林或工厂前哨
            self.create_pollution_effects()
        elif self.level == 9:  # 世界之树
            self.create_light_beams()
            self.create_magic_particles()

    def create_fog_effects(self):
        # 创建雾气效果
        for _ in range(10):
            fog = EnvironmentEffect('fog', random.randint(0, SCREEN_WIDTH * 2),
                                    random.randint(0, SCREEN_HEIGHT))
            self.environment_effects.append(fog)

    def create_water_effects(self):
        # 创建水波纹效果
        for tile in self.tile_list:
            if len(tile) >= 3 and tile[2] == "water":
                # 在水面上添加波纹效果
                water_effect = EnvironmentEffect('water_ripple', tile[1].x + self.tile_size // 2,
                                                 tile[1].y)
                self.environment_effects.append(water_effect)

    def create_pollution_effects(self):
        # 创建污染效果
        for tile in self.tile_list:
            if len(tile) >= 3 and tile[2] == "pollution":
                # 在污染区域添加污染颗粒效果
                pollution_effect = EnvironmentEffect('pollution', tile[1].x + self.tile_size // 2,
                                                     tile[1].y)
                self.environment_effects.append(pollution_effect)

    def create_light_beams(self):
        # 创建光束效果（用于世界之树关卡）
        for _ in range(5):
            light_beam = EnvironmentEffect('light_beam',
                                           random.randint(SCREEN_WIDTH // 2 - 100, SCREEN_WIDTH // 2 + 100),
                                           0)
            self.environment_effects.append(light_beam)

    def create_magic_particles(self):
        # 创建魔法粒子效果
        for _ in range(20):
            particle = EnvironmentEffect('magic_particle',
                                         random.randint(0, SCREEN_WIDTH * 2),
                                         random.randint(0, SCREEN_HEIGHT))
            self.environment_effects.append(particle)

    def check_collision(self, player_rect):
        # 检测玩家与地形的碰撞
        collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False}
        collision_tiles = []

        for tile in self.tile_list:
            if tile[1].colliderect(player_rect):
                collision_tiles.append(tile)

        return collision_tiles

    def clean_pollution(self, position, radius):
        # 清理指定位置附近的污染
        cleaned = False
        for tile in self.tile_list:
            if len(tile) >= 3 and tile[2] == "pollution":
                # 计算距离
                tile_center = (tile[1].x + self.tile_size // 2, tile[1].y + self.tile_size // 2)
                distance = ((position[0] - tile_center[0]) ** 2 + (position[1] - tile_center[1]) ** 2) ** 0.5

                if distance <= radius:
                    # 将污染块替换为草地
                    index = self.tile_list.index(tile)
                    new_img = self.grass_img
                    new_rect = tile[1].copy()
                    self.tile_list[index] = (new_img, new_rect)
                    cleaned = True

                    # 增加森林健康度
                    self.forest_health = min(self.forest_health + 1, self.max_level_health)

        return cleaned

    def plant_tree(self, position):
        # 在指定位置种植树木
        planted = False
        for tile in self.tile_list:
            if len(tile) < 3 and tile[0] == self.grass_img:  # 只在草地上种树
                if tile[1].collidepoint(position):
                    # 创建一棵新树
                    tree_size = (2, 3)  # (宽度, 高度) 单位为tile_size
                    tree = {
                        'img': pygame.Surface((tree_size[0] * self.tile_size, tree_size[1] * self.tile_size)),
                        'rect': pygame.Rect(tile[1].x, tile[1].y - tree_size[1] * self.tile_size,
                                            tree_size[0] * self.tile_size, tree_size[1] * self.tile_size),
                        'type': 'tree'
                    }
                    tree['img'].fill(GREEN)  # 简单的绿色表示树
                    self.collectibles.append(tree)
                    planted = True

                    # 增加森林健康度
                    self.forest_health = min(self.forest_health + 2, self.max_level_health)
                    break

        return planted

    def get_forest_health(self):
        # 返回当前森林健康度
        return self.forest_health

    def get_level_name(self):
        # 返回当前关卡名称
        return self.level_names.get(self.level, "未知区域")

    def is_position_solid(self, x, y):
        """检查指定位置是否是实体障碍物"""
        # 转换为瓦片坐标
        tile_x = int(x / TILE_SIZE)
        tile_y = int(y / TILE_SIZE)

        # 检查坐标是否在世界范围内
        if tile_x < 0 or tile_x >= self.world_width // TILE_SIZE or tile_y < 0 or tile_y >= self.world_height // TILE_SIZE:
            return True  # 世界边界外视为实体

        # 检查该位置是否有瓦片
        for tile in self.tile_list:
            if tile[1].collidepoint(x, y):
                return True

        return False

class EnvironmentEffect:
    def __init__(self, effect_type, x, y):
        self.effect_type = effect_type
        self.x = x
        self.y = y
        self.lifetime = random.randint(100, 300)  # 效果持续时间
        self.alpha = random.randint(100, 200)  # 透明度
        self.size = random.randint(10, 30)  # 效果大小
        self.speed = random.uniform(0.5, 1.5)  # 效果移动速度
        self.is_done = False

        # 根据效果类型设置颜色
        if effect_type == 'fog':
            self.color = (200, 200, 200, self.alpha)  # 灰白色雾气
        elif effect_type == 'water_ripple':
            self.color = (100, 150, 255, self.alpha)  # 蓝色水波纹
        elif effect_type == 'pollution':
            self.color = (150, 50, 150, self.alpha)  # 紫色污染
        elif effect_type == 'light_beam':
            self.color = (255, 255, 200, self.alpha)  # 黄色光束
        elif effect_type == 'magic_particle':
            self.color = (random.randint(100, 255),
                          random.randint(100, 255),
                          random.randint(100, 255),
                          self.alpha)  # 随机颜色的魔法粒子

    def update(self):
        # 更新效果状态
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.is_done = True
            return

        # 根据效果类型更新位置和状态
        if self.effect_type == 'fog':
            self.x += self.speed * random.uniform(-0.5, 0.5)
            self.y += self.speed * random.uniform(-0.3, 0.3)
            self.alpha = max(0, self.alpha - 0.5)
        elif self.effect_type == 'water_ripple':
            self.size += self.speed
            self.alpha = max(0, self.alpha - 1)
        elif self.effect_type == 'pollution':
            self.y -= self.speed * 0.2
            self.alpha = max(0, self.alpha - 0.5)
        elif self.effect_type == 'light_beam':
            self.alpha = 100 + 100 * abs(math.sin(self.lifetime * 0.05))
        elif self.effect_type == 'magic_particle':
            self.x += self.speed * random.uniform(-1, 1)
            self.y += self.speed * random.uniform(-1, 1)
            self.alpha = max(0, self.alpha - 0.5)

    def draw(self, screen, scroll):
        # 绘制效果
        if self.is_done:
            return

        # 创建透明表面
        effect_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        if self.effect_type == 'fog':
            pygame.draw.circle(effect_surface, self.color, (self.size // 2, self.size // 2), self.size // 2)
        elif self.effect_type == 'water_ripple':
            pygame.draw.circle(effect_surface, self.color, (self.size // 2, self.size // 2), self.size // 2, 2)
        elif self.effect_type == 'pollution':
            pygame.draw.circle(effect_surface, self.color, (self.size // 2, self.size // 2), self.size // 3)
        elif self.effect_type == 'light_beam':
            pygame.draw.polygon(effect_surface, self.color,
                                [(self.size // 2, 0), (0, self.size), (self.size, self.size)])
        elif self.effect_type == 'magic_particle':
            pygame.draw.circle(effect_surface, self.color, (self.size // 2, self.size // 2), self.size // 4)

        # 绘制到屏幕上
        screen.blit(effect_surface, (self.x - scroll[0], self.y - scroll[1]))