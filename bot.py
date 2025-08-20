"""
机器人模块

实现机器人的基本功能，包括移动、转向、传感器检测和动作执行。
机器人只能看到前方一格，必须通过传感器来了解环境。
"""

from typing import Tuple, Optional
from world import World, TileType


class Bot:
    """机器人类"""
    
    def __init__(self, world: World, x: int, y: int, direction: str = "N"):
        """
        初始化机器人
        
        Args:
            world: 世界对象
            x: 初始x坐标
            y: 初始y坐标
            direction: 初始朝向 (N, E, S, W)
        """
        self.world = world
        self.x = x
        self.y = y
        self.direction = direction
        self.have_key = False
        self.has_open_door = False
        self.steps_taken = 0
        self.max_steps = 1000  # 防止无限循环
        
    def get_pose(self) -> Tuple[int, int]:
        """获取机器人当前位置"""
        return (self.x, self.y)
    
    def get_direction(self) -> str:
        """获取机器人当前朝向"""
        return self.direction
    
    def is_on_key(self) -> bool:
        """检查机器人是否在钥匙上"""
        return self.world.isKey(self.x, self.y)
    
    def is_on_door(self) -> bool:
        """检查机器人是否在门上"""
        return self.world.isDoor(self.x, self.y)
    
    def is_on_exit(self) -> bool:
        """检查机器人是否在出口"""
        return self.world.isExit(self.x, self.y)
    
    def front_is_clear(self) -> bool:
        """检查机器人前方是否清晰（不是墙）"""
        return self.world.isFrontClear(self.x, self.y, self.direction)
    
    def at_key(self) -> bool:
        """检查机器人是否在钥匙处（别名）"""
        return self.is_on_key()
    
    def at_door(self) -> bool:
        """检查机器人是否在门处（别名）"""
        return self.is_on_door()
    
    def at_exit(self) -> bool:
        """检查机器人是否在出口处（别名）"""
        return self.is_on_exit()
    
    def move_forward(self) -> bool:
        """
        向前移动一格
        
        Returns:
            bool: 移动是否成功
        """
        if self.steps_taken >= self.max_steps:
            raise RuntimeError("机器人移动步数超过限制")
            
        if not self.front_is_clear():
            return False  # 前方是墙，无法移动
            
        # 计算新位置
        new_x, new_y = self.world.getFrontPosition(self.x, self.y, self.direction)
        
        # 更新位置
        old_x, old_y = self.x, self.y
        self.x, self.y = new_x, new_y
        
        # 更新世界状态
        self.world.updateBot(self.x, self.y, self.direction)
        
        self.steps_taken += 1
        return True
    
    def turn_left(self) -> None:
        """向左转"""
        if self.direction == "N":
            self.direction = "W"
        elif self.direction == "W":
            self.direction = "S"
        elif self.direction == "S":
            self.direction = "E"
        elif self.direction == "E":
            self.direction = "N"
        
        # 更新世界状态
        self.world.updateBot(self.x, self.y, self.direction)
    
    def turn_right(self) -> None:
        """向右转"""
        if self.direction == "N":
            self.direction = "E"
        elif self.direction == "E":
            self.direction = "S"
        elif self.direction == "S":
            self.direction = "W"
        elif self.direction == "W":
            self.direction = "N"
        
        # 更新世界状态
        self.world.updateBot(self.x, self.y, self.direction)
    
    def pick_key(self) -> bool:
        """
        拾取当前格的钥匙
        
        Returns:
            bool: 拾取是否成功
        """
        if self.is_on_key():
            self.world.updateKey(self.x, self.y)
            self.have_key = True
            return True
        return False
    
    def open_door(self) -> bool:
        """
        打开门
        
        Returns:
            bool: 开门是否成功
        """
        if self.is_on_door() and self.have_key:
            self.world.updateDoor(self.x, self.y)
            self.has_open_door = True
            return True
        return False
    
    def look(self) -> Optional[TileType]:
        """
        查看前方一格的瓦片类型
        
        Returns:
            TileType: 前方瓦片类型，如果超出边界则返回None
        """
        return self.world.getFrontTile(self.x, self.y, self.direction)
    
    def get_status(self) -> dict:
        """获取机器人当前状态"""
        return {
            'x': self.x,
            'y': self.y,
            'direction': self.direction,
            'have_key': self.have_key,
            'has_open_door': self.has_open_door,
            'steps_taken': self.steps_taken,
            'on_key': self.is_on_key(),
            'on_door': self.is_on_door(),
            'on_exit': self.is_on_exit(),
            'front_clear': self.front_is_clear()
        }
    
    def reset(self, x: int, y: int, direction: str = "N"):
        """重置机器人状态"""
        self.x = x
        self.y = y
        self.direction = direction
        self.have_key = False
        self.has_open_door = False
        self.steps_taken = 0
        self.world.updateBot(self.x, self.y, self.direction)
    
    def can_exit(self) -> bool:
        """检查机器人是否可以离开（在出口处）"""
        return self.is_on_exit()
    
    def exit(self) -> bool:
        """
        离开世界
        
        Returns:
            bool: 是否成功离开
        """
        if self.can_exit():
            return True
        return False
    
    def get_front_position(self) -> Tuple[int, int]:
        """获取机器人前方的位置坐标"""
        return self.world.getFrontPosition(self.x, self.y, self.direction)
    
    def get_front_tile(self) -> Optional[TileType]:
        """获取机器人前方的瓦片类型"""
        return self.world.getFrontTile(self.x, self.y, self.direction)
    
    def is_stuck(self) -> bool:
        """检查机器人是否被困住（无法移动）"""
        # 检查四个方向是否都被墙包围
        directions = ["N", "E", "S", "W"]
        for direction in directions:
            if self.world.isFrontClear(self.x, self.y, direction):
                return False
        return True
    
    def get_available_moves(self) -> list:
        """获取可用的移动方向"""
        available = []
        directions = ["N", "E", "S", "W"]
        for direction in directions:
            if self.world.isFrontClear(self.x, self.y, direction):
                available.append(direction)
        return available 