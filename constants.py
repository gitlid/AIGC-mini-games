import pygame
from enum import Enum

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRAVITY = 0.8
SCROLL_THRESHOLD = 400
TILE_SIZE = 50

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
LIGHT_GREEN = (76, 175, 80)
DARK_BROWN = (121, 85, 72)
LIGHT_BLUE = (100, 200, 255)
LIGHT_GRAY = (200, 200, 200)
MEDIUM_GRAY = (150, 150, 150)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PINK = (255, 192, 203)
DARK_GREEN = (0, 100, 0)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)


# 游戏状态
class GameState(Enum):
    MAIN_MENU = 0
    LEVEL_SELECT = 1  # 新增关卡选择状态
    CHARACTER_SELECT = 2  # 保留但调整编号
    PLAYING = 3  # 调整编号
    PAUSED = 4  # 调整编号
    GAME_OVER = 5  # 调整编号
    VICTORY = 6  # 调整编号
    CUTSCENE = 7  # 调整编号
    TUTORIAL = 8  # 调整编号
    SETTINGS = 9  # 调整编号

# 角色类型
class CharacterType(Enum):
    LIA = 0
    KARN = 1

# 敌人类型
class EnemyType(Enum):
    LOGGER = 0
    POLLUTER = 1
    MACHINE = 2
    FLAMETHROWER = 3
    BOSS = 4

# 字体初始化
# 字体初始化 - 修改为更可靠的中文字体方案
try:
    # 尝试加载微软雅黑字体（Windows系统自带）
    font_small = pygame.font.Font("msyh.ttc", 24)
    font_medium = pygame.font.Font("msyh.ttc", 32)
    font_large = pygame.font.Font("msyh.ttc", 48)
    title_font = pygame.font.Font("msyh.ttc", 72)
except:
    # 备用方案：使用系统默认中文字体
    try:
        font_small = pygame.font.SysFont("simhei", 24)
        font_medium = pygame.font.SysFont("simhei", 32)
        font_large = pygame.font.SysFont("simhei", 48)
        title_font = pygame.font.SysFont("simhei", 72)
    except:
        # 最终备用方案：使用系统默认字体（可能不支持中文）
        font_small = pygame.font.SysFont(None, 24)
        font_medium = pygame.font.SysFont(None, 32)
        font_large = pygame.font.SysFont(None, 48)
        title_font = pygame.font.SysFont(None, 72)

# 键位定义
KEY_UP = pygame.K_w
KEY_LEFT = pygame.K_a
KEY_DOWN = pygame.K_s
KEY_RIGHT = pygame.K_d
KEY_JUMP = pygame.K_SPACE
KEY_ATTACK = pygame.K_j
KEY_SKILL_1 = pygame.K_1
KEY_SKILL_2 = pygame.K_2
KEY_SKILL_3 = pygame.K_3
KEY_PAUSE = pygame.K_ESCAPE

# 游戏关卡常量
MAX_LEVELS = 9  # 3章节, 每章3关
