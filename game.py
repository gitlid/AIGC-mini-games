#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pygame
import sys
import random
from enum import Enum

from collectibles_system import CollectibleManager
from constants import *
from characters import Lia, Karn, CharacterType
from enemies import create_enemy, GreedyMerchant
from world import World
from ui import GameUI, MainMenuUI, CharacterSelectUI, PauseMenuUI, GameOverUI, VictoryUI, CutsceneUI, TutorialUI, \
    SettingsUI, LevelSelectUI
from particles import ParticleSystem


class Game:
    def __init__(self):
        # 初始化 Pygame
        pygame.init()
        pygame.mixer.init()

        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("森林守护者")
        self.clock = pygame.time.Clock()

        # 加载游戏字体
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # 游戏状态
        self.state = GameState.MAIN_MENU

        # 游戏UI
        self.main_menu_ui = MainMenuUI()
        self.level_select_ui = LevelSelectUI()  # 新增关卡选择UI
        self.character_select_ui = CharacterSelectUI()
        self.pause_menu_ui = None  # 将在游戏开始时初始化
        self.game_over_ui = None
        self.victory_ui = None
        self.cutscene_ui = None
        self.tutorial_ui = None  # 新增教程UI
        self.settings_ui = None  # 新增设置UI

        # 游戏相关变量
        self.player = None
        self.player_character_type = None
        self.world = None
        self.enemies = []
        self.particle_system = ParticleSystem()
        self.game_ui = None
        self.level = 1
        self.max_level = 9  # 总关卡数
        self.background = None

        # 游戏控制变量
        self.scroll = [0, 0]  # 屏幕滚动偏移
        self.moving_left = False
        self.moving_right = False
        self.running = True  # 游戏主循环控制

        # 音乐和音效相关变量
        self.current_music = None
        self.music_volume = 0.7
        self.sound_volume = 0.8

        # 加载游戏背景
        self.load_background()

        # 加载游戏音效和音乐
        self.load_sounds()

        # 开始背景音乐
        self.play_music("main_menu")

        # 开发者模式
        self.dev_mode = False
        self.dev_mode_message_timer = 0

        # 收集品系统
        self.collectible_manager = CollectibleManager()
        self.score_factor = 1

    def load_background(self, level=None):
        """加载背景图片，如果没有指定关卡则加载默认背景"""
        if level is None:
            # 主菜单背景
            background_file = "backgrounds/main_menu.png"
        else:
            # 关卡背景
            background_file = f"backgrounds/level_{level}.jpg"

        try:
            # 尝试加载背景图片
            if os.path.exists(background_file):
                self.background = pygame.image.load(background_file)
                # 缩放到屏幕大小
                self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"成功加载背景: {background_file}")
            else:
                print(f"背景文件不存在: {background_file}，使用默认背景")
                # 创建默认背景
                self.create_default_background()
        except pygame.error as e:
            print(f"加载背景图片失败: {e}，使用默认背景")
            self.create_default_background()

    def create_default_background(self):
        """创建默认背景"""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill((100, 150, 255))  # 蓝天背景

        # 添加一些随机的云彩
        for _ in range(10):
            cloud = pygame.Surface((random.randint(50, 200), random.randint(30, 60)))
            cloud.fill((255, 255, 255))
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 3)
            self.background.blit(cloud, (x, y))
    def load_sounds(self):
        """加载游戏音效和音乐"""
        # 音效文件路径字典
        sound_files = {
            "jump": "sounds/Jump150.wav",
            "attack": "sounds/Hit1.wav",
            "hurt": "sounds/Hit53.wav",
            "skill": "sounds/Boom6.wav",
            "menu_select": "sounds/click.wav",
            "level_complete": "sounds/Random57.wav"
        }

        # 音乐文件路径字典
        self.music_files = {
            "main_menu": "music/s0dow-597fu.ogg",
            "playing": "music/l0wlu-2z5di.ogg",
            "victory": "music/qo968-a9lhx.ogg",
            "game_over": "music/xthue-k2v1k.ogg"
        }

        # 加载音效
        self.sounds = {}
        for sound_name, file_path in sound_files.items():
            try:
                # 检查文件是否存在
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sound_volume)
                    self.sounds[sound_name] = sound
                    print(f"成功加载音效: {sound_name}")
                else:
                    print(f"音效文件不存在: {file_path}")
                    self.sounds[sound_name] = None
            except pygame.error as e:
                print(f"加载音效失败 {sound_name}: {e}")
                self.sounds[sound_name] = None

    def play_music(self, track):
        """播放背景音乐"""
        if track in self.music_files:
            music_file = self.music_files[track]

            # 检查文件是否存在
            if not os.path.exists(music_file):
                print(f"音乐文件不存在: {music_file}")
                return

            try:
                # 如果当前播放的音乐和要播放的相同，则不重复播放
                if self.current_music == track and pygame.mixer.music.get_busy():
                    return

                # 停止当前音乐
                pygame.mixer.music.stop()

                # 加载并播放新音乐
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)

                # 根据音乐类型设置循环次数
                if track in ["main_menu", "playing"]:
                    pygame.mixer.music.play(-1)  # 无限循环
                else:
                    pygame.mixer.music.play(0)  # 播放一次

                self.current_music = track
                print(f"播放音乐: {track}")

            except pygame.error as e:
                print(f"播放音乐失败 {track}: {e}")
        else:
            print(f"未知的音乐轨道: {track}")

    def play_sound(self, sound_name):
        """播放音效"""
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                # 播放音效
                self.sounds[sound_name].play()
            except pygame.error as e:
                print(f"播放音效失败 {sound_name}: {e}")
        else:
            # 如果音效不存在，可以选择播放默认音效或忽略
            print(f"音效不存在或未加载: {sound_name}")

    def set_music_volume(self, volume):
        """设置音乐音量 (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sound_volume(self, volume):
        """设置音效音量 (0.0 - 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        # 更新所有已加载音效的音量
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.sound_volume)

    def stop_music(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
        self.current_music = None

    def pause_music(self):
        """暂停背景音乐"""
        pygame.mixer.music.pause()

    def resume_music(self):
        """恢复背景音乐"""
        pygame.mixer.music.unpause()

    def create_level(self, level):
        # 清空现有的敌人
        self.enemies = []

        # 创建世界
        self.world = World(level)

        # 加载对应关卡的背景
        self.load_background(level)


        # 创建角色
        if self.player_character_type == CharacterType.LIA:
            self.player = Lia(100, 200, 3.0)
        else:
            self.player = Karn(100, 200, 3.0)

        # 设置角色的世界引用
        self.player.world = self.world

        # 创建游戏UI
        self.game_ui = GameUI(self.player)

        # 创建敌人
        self.create_enemies(level)

        # 生成关卡收集品
        self.collectible_manager.spawn_level_collectibles(level, self.world.world_width)

        # 初始化屏幕滚动
        self.scroll = [0, 0]

    def create_enemies(self, level):
        # 根据关卡创建不同的敌人
        if level == 1:
            # 第一关：几个简单的敌人
            for i in range(5):
                x = random.randint(500, self.world.world_width - 100)
                y = 300
                enemy_type = random.randint(0, 1)  # 0：伐木工，1：污染者
                self.enemies.append(create_enemy(x, y, enemy_type, 1.0))
        elif level == 2:
            # 第二关：更多更强的敌人
            for i in range(8):
                x = random.randint(500, self.world.world_width - 100)
                y = 300
                enemy_type = random.randint(0, 2)  # 0：伐木工，1：污染者，2：伐木机
                self.enemies.append(create_enemy(x, y, enemy_type, 1.0))
        elif level == 3:
            # 第三关：BOSS关
            boss = create_enemy(800, 300, 4, 2.0)  # 贪婪商人
            self.enemies.append(boss)

            # 再添加几个小怪
            for i in range(3):
                x = random.randint(500, self.world.world_width - 100)
                y = 300
                enemy_type = random.randint(2, 3)  # 2：伐木机，3：火焰喷射器
                self.enemies.append(create_enemy(x, y, enemy_type, 1.0))

        else:
            for i in range(level//3):
                boss = create_enemy(random.randint(self.world.world_width//2 + 100, self.world.world_width - 100), 300, 4, 2.0)  # 贪婪商人
                boss.health = random.randint(300, 500)
                boss.max_health = boss.health

                boss.shield_health = random.randint(100, 300)
                boss.shield_max_health = boss.shield_health
                boss.strength = 20
                self.enemies.append(boss)
            for i in range(level):
                x = random.randint(500, self.world.world_width - 100)
                y = 300
                enemy_type = random.randint(0, 3)  # 0：伐木工，1：污染者，2：伐木机，3：火焰喷射器
                self.enemies.append(create_enemy(x, y, enemy_type, 1.0))


    def update_scroll(self):
        # 计算目标滚动位置 - 让玩家保持在屏幕中心
        target_scroll_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_scroll_y = self.player.rect.centery - SCREEN_HEIGHT // 4 * 3

        # 平滑滚动 - 可以调整系数来改变跟随速度（0.1更快，0.05较慢）
        self.scroll[0] += (target_scroll_x - self.scroll[0]) * 0.05  # 提高系数使跟随更紧密
        self.scroll[1] += (target_scroll_y - self.scroll[1]) * 0.05

        # 限制滚动范围，防止超出地图边界
        if self.scroll[0] < 0:
            self.scroll[0] = 0
        if self.scroll[1] < 0:
            self.scroll[1] = 0

        # 计算最大滚动限制
        # 注意：确保world.tile_size是正确定义的，并且世界地图有合适的尺寸
        max_scroll_x = len(self.world.tile_list[0]) * self.world.tile_size - SCREEN_WIDTH
        max_scroll_y = len(self.world.tile_list) * self.world.tile_size - SCREEN_HEIGHT

        # 防止滚动超出右/下边界
        # if self.scroll[0] > max_scroll_x:
        #     self.scroll[0] = max_scroll_x
        # if self.scroll[1] > max_scroll_y:
        #     self.scroll[1] = max_scroll_y

    def check_level_complete(self):
        # 检查关卡是否完成
        all_enemies_dead = True
        for enemy in self.enemies:
            if enemy.alive:
                all_enemies_dead = False
                break

        if all_enemies_dead:
            if self.level < self.max_level:
                # 进入下一关
                self.level += 1
                self.create_level(self.level)
                # 播放关卡完成音效
                self.play_sound("level_complete")
            else:
                # 通关游戏
                self.state = GameState.VICTORY
                self.victory_ui = VictoryUI()
                # 播放胜利音乐
                self.play_music("victory")

    def check_game_over(self):
        # 检查游戏是否结束
        if (self.player.health <= 0 or self.world.forest_health <= 0) and not self.dev_mode:
            self.player.alive = False
            self.state = GameState.GAME_OVER
            self.game_over_ui = GameOverUI()
            # 播放游戏结束音乐
            self.play_music("game_over")

    def handle_events(self):
        # 处理游戏事件
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 根据游戏状态处理不同的事件
            if self.state == GameState.MAIN_MENU:
                self.handle_main_menu_events(event, mouse_pos)
            elif self.state == GameState.LEVEL_SELECT:  # 新增关卡选择状态处理
                self.handle_level_select_events(event, mouse_pos)
            elif self.state == GameState.CHARACTER_SELECT:
                self.handle_character_select_events(event, mouse_pos)
            elif self.state == GameState.PLAYING:
                self.handle_playing_events(event, mouse_pos)
            elif self.state == GameState.PAUSED:
                self.handle_paused_events(event, mouse_pos)
            elif self.state == GameState.GAME_OVER:
                self.handle_game_over_events(event, mouse_pos)
            elif self.state == GameState.VICTORY:
                self.handle_victory_events(event, mouse_pos)
            elif self.state == GameState.TUTORIAL:
                self.handle_tutorial_events(event, mouse_pos)
            elif self.state == GameState.SETTINGS:  # 新增设置状态处理
                self.handle_settings_events(event, mouse_pos)

    def handle_tutorial_events(self, event, mouse_pos):
        # 处理教程事件
        result = self.tutorial_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")
            if result in ["prev", "next"]:
                # 翻页音效已经播放
                pass
            elif result == "skip":
                self.state = GameState.CHARACTER_SELECT
            elif result == "start":
                self.state = GameState.CHARACTER_SELECT

    def handle_main_menu_events(self, event, mouse_pos):
        # 处理主菜单事件
        if event.type == pygame.MOUSEMOTION:
            for i, button in enumerate(self.main_menu_ui.buttons):
                button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.main_menu_ui.buttons[0].is_clicked(mouse_pos, event):  # 开始游戏
                # self.state = GameState.CHARACTER_SELECT
                self.state = GameState.TUTORIAL  # 改为进入教程
                self.tutorial_ui = TutorialUI()
                self.play_sound("menu_select")
            elif self.main_menu_ui.buttons[1].is_clicked(mouse_pos, event):  # 选择关卡
                self.state = GameState.LEVEL_SELECT  # 改为进入关卡选择
                self.play_sound("menu_select")
            elif self.main_menu_ui.buttons[2].is_clicked(mouse_pos, event):  # 设置
                self.state = GameState.SETTINGS  # 进入设置菜单
                if self.settings_ui is None:
                    self.settings_ui = SettingsUI()
                # 同步当前音量设置到UI
                self.settings_ui.music_volume = self.music_volume
                self.settings_ui.sound_volume = self.sound_volume
                self.play_sound("menu_select")
            elif self.main_menu_ui.buttons[3].is_clicked(mouse_pos, event):  # 退出
                self.play_sound("menu_select")
                pygame.quit()
                sys.exit()

    def handle_character_select_events(self, event, mouse_pos):
        # 处理角色选择事件
        result = self.character_select_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")
            if result == "lia":
                self.player_character_type = CharacterType.LIA
                # self.level = 1
                self.create_level(self.level)
                self.state = GameState.PLAYING
                self.play_music("playing")
            elif result == "karn":
                self.player_character_type = CharacterType.KARN
                # self.level = 1
                self.create_level(self.level)
                self.state = GameState.PLAYING
                self.play_music("playing")
            elif result == "back":
                self.state = GameState.MAIN_MENU

    def handle_playing_events(self, event, mouse_pos):
        # 处理游戏中的事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.moving_left = True
            if event.key == pygame.K_d:
                self.moving_right = True
            if event.key == pygame.K_SPACE:
                if not self.player.in_air:
                    self.play_sound("jump")
                self.player.jump = True
            if event.key == pygame.K_j:
                self.player.attack(self.enemies, self.particle_system, self.dev_mode, self.score_factor)
                self.play_sound("attack")
            if event.key == pygame.K_1:
                skill_used = False
                if self.player.character_type == CharacterType.LIA:
                    skill_used = self.player.skill_1(self.enemies, self.particle_system, self.score_factor)
                else:
                    skill_used = self.player.skill_1(self.enemies, self.particle_system, self.score_factor)
                if skill_used:
                    self.play_sound("skill")
            if event.key == pygame.K_2:
                skill_used = False
                if self.player.character_type == CharacterType.LIA:
                    skill_used = self.player.skill_2(self.world, self.particle_system, self.score_factor)
                else:
                    skill_used = self.player.skill_2(self.particle_system, self.score_factor)
                if skill_used:
                    self.play_sound("skill")
            if event.key == pygame.K_3:
                skill_used = False
                if self.player.character_type == CharacterType.LIA:
                    skill_used = self.player.skill_3(self.enemies, self.particle_system, self.score_factor)
                else:
                    skill_used = self.player.skill_3(self.particle_system, self.score_factor)
                if skill_used:
                    self.play_sound("skill")
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
                self.pause_menu_ui = PauseMenuUI()

            # 切换开发者模式 - 使用F10键
            if event.key == pygame.K_F10:
                self.dev_mode = not self.dev_mode
                self.dev_mode_message_timer = 180  # 显示3秒(180帧)的开发者模式提示
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
                self.pause_menu_ui = PauseMenuUI()
                self.pause_music()  # 暂停音乐

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
            if event.key == pygame.K_d:
                self.moving_right = False

        # 处理游戏UI事件
        if self.game_ui:
            self.game_ui.check_hover(mouse_pos)
            ui_action = self.game_ui.handle_click(mouse_pos, event)

            # 添加收集UI事件处理
            collection_action = self.game_ui.handle_collection_ui_events(event, mouse_pos)
            if collection_action == "toggle_collection_details":
                self.play_sound("menu_select")

            if ui_action:
                if ui_action == "pause":
                    self.play_sound("menu_select")
                    self.state = GameState.PAUSED
                    self.pause_menu_ui = PauseMenuUI()
                elif ui_action.startswith("skill_"):
                    skill_num = int(ui_action.split("_")[1])
                    if skill_num == 1:
                        if self.player.character_type == CharacterType.LIA:
                            self.player.skill_1(self.enemies, self.particle_system)
                        else:
                            self.player.skill_1(self.enemies, self.particle_system)
                    elif skill_num == 2:
                        if self.player.character_type == CharacterType.LIA:
                            self.player.skill_2(self.world, self.particle_system)
                        else:
                            self.player.skill_2(self.particle_system)
                    elif skill_num == 3:
                        if self.player.character_type == CharacterType.LIA:
                            self.player.skill_3(self.enemies, self.particle_system)
                        else:
                            self.player.skill_3(self.particle_system)
                    self.play_sound("skill")

    # 在handle_paused_events方法中添加音乐暂停/恢复
    def handle_paused_events(self, event, mouse_pos):
        # 处理暂停菜单事件
        result = self.pause_menu_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")
            if result == "resume":
                self.state = GameState.PLAYING
                self.resume_music()  # 恢复音乐
            elif result == "main_menu":
                self.state = GameState.MAIN_MENU
                self.play_music("main_menu")
            elif result == "quit":
                pygame.quit()
                sys.exit()

    def handle_game_over_events(self, event, mouse_pos):
        # 处理游戏结束事件
        result = self.game_over_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")
            if result == "retry":
                # 重新开始当前关卡
                self.create_level(self.level)
                self.state = GameState.PLAYING
                self.play_music("playing")
            elif result == "main_menu":
                self.state = GameState.MAIN_MENU
                self.play_music("main_menu")

    def handle_victory_events(self, event, mouse_pos):
        # 处理胜利事件
        result = self.victory_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")
            if result == "main_menu":
                self.state = GameState.MAIN_MENU
                self.play_music("main_menu")

    def handle_settings_events(self, event, mouse_pos):
        """处理设置菜单事件"""
        if self.settings_ui is None:
            return

        result = self.settings_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")

            if result == "apply":
                # 应用设置
                self.apply_settings()
            elif result == "reset":
                # 重置设置
                self.settings_ui.reset_settings()
                self.apply_settings()
            elif result == "back":
                # 返回主菜单
                self.state = GameState.MAIN_MENU
            elif result == "resolution_change":
                # 分辨率改变，暂时不做处理（需要重启游戏）
                pass
            elif result == "fullscreen_toggle":
                # 全屏切换，暂时不做处理
                pass

    # 新增关卡选择事件处理方法：
    def handle_level_select_events(self, event, mouse_pos):
        """处理关卡选择事件"""
        result = self.level_select_ui.handle_event(event, mouse_pos)
        if result:
            self.play_sound("menu_select")
            if result == "back":
                self.state = GameState.MAIN_MENU
            elif isinstance(result, dict):  # 角色和关卡选择完成
                self.level = result["level"]

                self.state = GameState.CHARACTER_SELECT

    # 6. 新增应用设置方法
    def apply_settings(self):
        """应用设置更改"""
        if self.settings_ui is None:
            return

        # 应用音量设置
        self.set_music_volume(self.settings_ui.music_volume)
        self.set_sound_volume(self.settings_ui.sound_volume)

        # 这里可以添加其他设置的应用逻辑
        print(f"设置已应用: 音乐音量={int(self.music_volume * 100)}%, 音效音量={int(self.sound_volume * 100)}%")

    def update(self):
        # 更新游戏状态
        if self.state == GameState.PLAYING:
            # 开发者模式提示计时器
            if self.dev_mode_message_timer > 0:
                self.dev_mode_message_timer -= 1
            # 更新粒子系统
            particles_to_draw = list(self.particle_system.update())

            # 更新玩家
            self.player.move(self.moving_left, self.moving_right, self.world, self.enemies, self.particle_system, self.dev_mode, self.score_factor)
            self.player.update_animation()

            # 更新敌人
            for enemy in self.enemies:
                if enemy.alive:
                    # enemy.move(self.world, self.player, self.particle_system)
                    # enemy.update_animation()
                    enemy.update(self.world, self.player, self.particle_system, )
                    if isinstance(enemy, GreedyMerchant):
                        if enemy.should_spawn_minions is True:
                            for _ in range(random.randint(2, 4)):
                                x = enemy.rect.centerx + random.randint(-100, 100)
                                y = 300
                                enemy_type = random.randint(0, 3)  # 0：伐木工，1：污染者，2：伐木机，3：火焰喷射器
                                self.enemies.append(create_enemy(x, y, enemy_type, 1.0))
                            enemy.should_spawn_minions = False

            # 更新收集品 - 记录收集前的数量
            prev_collected = self.collectible_manager.collection_stats['total_collected']
            self.collectible_manager.update(self.player, self.particle_system)
            # 检查是否有新的收集品被收集
            new_collected = self.collectible_manager.collection_stats['total_collected']
            self.score_factor = self.collectible_manager.collection_stats["score"] // 100
            if new_collected > prev_collected:
                # 播放收集音效（如果有的话）
                self.play_sound("menu_select")  # 临时使用菜单选择音效

            if self.player.hit:
                self.play_sound("hurt")
                self.player.hit = False
            # 更新屏幕滚动
            self.update_scroll()

            # 检查游戏是否结束
            self.check_game_over()

            # 检查关卡是否完成
            self.check_level_complete()
            # 如果开发者模式开启，给玩家补满生命和魔法
            if self.dev_mode:
                self.player.health = self.player.max_health
                self.player.magic = self.player.max_magic
                self.player.invulnerability = 2

    def draw(self):
        # 清屏
        self.screen.fill((0, 0, 0))

        # 绘制背景
        self.screen.blit(self.background, (0, 0))

        if self.state == GameState.MAIN_MENU:
            # 绘制主菜单
            self.main_menu_ui.draw(self.screen)

        elif self.state == GameState.LEVEL_SELECT:  # 新增关卡选择界面绘制
            # 绘制关卡选择界面
            self.level_select_ui.draw(self.screen)


        elif self.state == GameState.CHARACTER_SELECT:
            # 绘制角色选择界面
            self.character_select_ui.draw(self.screen)

        elif self.state == GameState.PLAYING:
            # 绘制世界
            self.world.draw(self.screen, self.scroll)

            # 绘制敌人
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.draw(self.screen, self.scroll)

            # 绘制收集品
            self.collectible_manager.draw(self.screen, self.scroll)

            # 绘制玩家
            self.player.draw(self.screen, self.scroll)

            # 绘制粒子效果
            for particle in self.particle_system.particles:
                pygame.draw.rect(self.screen, particle.color,
                                 (particle.x - self.scroll[0], particle.y - self.scroll[1],
                                  particle.size, particle.size))

            # 绘制UI
            self.game_ui.update()
            self.game_ui.draw(self.screen)

            # 显示开发者模式提示
            if self.dev_mode:
                dev_text = self.font_medium.render("开发者模式: 已启用", True, (255, 255, 0))
                self.screen.blit(dev_text, (SCREEN_WIDTH // 4 * 3 - dev_text.get_width() - 10, 10))
            elif self.dev_mode_message_timer > 0:
                dev_text = self.font_medium.render("开发者模式: 已禁用", True, (255, 255, 0))
                self.screen.blit(dev_text, (SCREEN_WIDTH // 4 * 3 - dev_text.get_width() - 10, 10))

            # 绘制UI - 传递收集管理器
            self.game_ui.update()
            self.game_ui.draw(self.screen, self.collectible_manager)  # 添加collection_manager参数

        elif self.state == GameState.PAUSED:
            # 绘制世界（灰暗）
            self.world.draw(self.screen, self.scroll)

            # 绘制暂停菜单
            self.pause_menu_ui.draw(self.screen)

        elif self.state == GameState.GAME_OVER:
            # 绘制世界（灰暗）
            self.world.draw(self.screen, self.scroll)

            # 绘制游戏结束界面
            self.game_over_ui.draw(self.screen)

        elif self.state == GameState.VICTORY:
            # 绘制胜利界面
            self.victory_ui.draw(self.screen)

        elif self.state == GameState.TUTORIAL:
            # 绘制教程界面
            self.tutorial_ui.draw(self.screen)

        elif self.state == GameState.SETTINGS:  # 新增设置界面绘制
            # 绘制设置界面
            if self.settings_ui:
                self.settings_ui.draw(self.screen)

        # 更新显示
        pygame.display.flip()

    def run(self):
        # 游戏主循环
        while self.running:
            # 处理事件
            self.handle_events()

            # 更新游戏状态
            self.update()

            # 绘制游戏
            self.draw()

            # 控制帧率
            self.clock.tick(60)




if __name__ == "__main__":
    game = Game()
    game.run()
