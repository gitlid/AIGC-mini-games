#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from game import Game

def main():
    """游戏启动入口主函数"""
    try:
        # 初始化游戏对象
        game = Game()
        # 运行游戏主循环
        game.run()
    except Exception as e:
        # 打印错误信息
        print(f"游戏发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保正确退出pygame
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
