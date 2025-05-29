import pygame
import random


class Particle:
    def __init__(self, x, y, *args, **kwargs):
        self.x = x
        self.y = y

        # 处理不同的参数传递方式
        if len(args) >= 4:
            # 原始方式: (x, y, color, size, speed, life)
            self.color = args[0]
            self.size = args[1]
            speed = args[2]
            self.life = args[3]
            self.speed_x = random.uniform(-speed, speed)
            self.speed_y = random.uniform(-speed, speed)
        elif len(args) >= 2:
            # create_collect_effect 方式: (x, y, dx, dy, color, life, size)
            self.speed_x = args[0]
            self.speed_y = args[1]
            if len(args) >= 5:
                self.color = args[2]
                self.life = args[3]
                self.size = args[4]
            else:
                # create_attract_particle 方式: (x, y, dx, dy, color, life, size)
                self.color = kwargs.get('color', (255, 255, 255))
                self.life = kwargs.get('life', 30)
                self.size = kwargs.get('size', 5)
        else:
            # 使用关键字参数
            self.color = kwargs.get('color', (255, 255, 255))
            self.size = kwargs.get('size', 5)
            speed = kwargs.get('speed', 2)
            self.life = kwargs.get('life', 30)
            self.speed_x = kwargs.get('speed_x', random.uniform(-speed, speed))
            self.speed_y = kwargs.get('speed_y', random.uniform(-speed, speed))

        self.initial_life = self.life

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        # 粒子逐渐变小和变透明
        ratio = self.life / self.initial_life
        current_size = self.size * ratio
        alpha = int(255 * ratio)
        current_color = (*self.color[:3], alpha) if len(self.color) > 3 else (*self.color, alpha)
        return current_size, current_color

    def is_dead(self):
        return self.life <= 0


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particles(self, x, y, color, count=20, size=5, speed=2, life=30):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, size, speed, life))

    def update(self):
        self.particles = [p for p in self.particles if not p.is_dead()]
        for particle in self.particles:
            current_size, current_color = particle.update()
            yield particle, current_size, current_color
    
    def draw(self, surface, scroll=(0, 0)):
        for particle, current_size, current_color in self.update():
            pygame.draw.circle(
                surface, 
                current_color, 
                (int(particle.x - scroll[0]), int(particle.y - scroll[1])), 
                int(current_size)
            )

    """扩展粒子系统以支持收集品效果"""

    # 添加收集品相关的粒子效果方法
    def create_collect_effect(self, x, y, color, rarity_level):
        """创建收集效果"""
        particle_count = 5 + rarity_level * 3

        for _ in range(particle_count):
            # 向上飞散的粒子
            dx = random.uniform(-3, 3)
            dy = random.uniform(-8, -2)

            # 使用关键字参数确保兼容性
            particle = Particle(
                x + random.uniform(-10, 10),
                y + random.uniform(-10, 10),
                speed_x=dx,
                speed_y=dy,
                color=color,
                life=30 + rarity_level * 10,
                size=3 + rarity_level
            )
            self.particles.append(particle)

    def create_attract_particle(self, start_x, start_y, target_x, target_y):
        """创建磁性吸引粒子"""
        particle = Particle(
            start_x, start_y,
            speed_x=0,
            speed_y=0,
            color=(100, 255, 255),
            life=20,
            size=2
        )
        # 可以添加特殊的吸引逻辑
        self.particles.append(particle)