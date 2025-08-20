"""
世界模型模块

实现2D网格世界，包含地板、墙壁、钥匙、门和出口。
管理世界状态和机器人位置更新。
"""

from typing import List, Tuple, Optional
from enum import Enum


class TileType(Enum):
    """瓦片类型枚举"""
    FLOOR = "FLOOR"      # 地板
    WALL = "WALL"        # 墙壁
    KEY = "KEY"          # 钥匙
    DOOR = "DOOR"        # 门
    EXIT = "EXIT"        # 出口


class World:
    """2D网格世界类"""
    
    def __init__(self):
        self.grid: List[List[TileType]] = []
        self.width: int = 0
        self.height: int = 0
        self.bot_x: int = 0
        self.bot_y: int = 0
        self.bot_direction: str = "N"  # N, E, S, W
        self.keys_collected: int = 0
        self.doors_opened: int = 0
        
    def setWorld(self, map_definition: List[List[str]], bot_start: Tuple[int, int], bot_direction: str = "N") -> Tuple['World', dict]:
        """
        初始化世界地图和机器人初始状态
        
        Args:
            map_definition: 字符串列表，每个字符串代表一行地图
            bot_start: 机器人起始位置 (x, y)
            bot_direction: 机器人初始朝向
            
        Returns:
            (world, bot_state): 世界对象和机器人初始状态
        """
        self.height = len(map_definition)
        self.width = len(map_definition[0]) if map_definition else 0
        
        # 初始化网格
        self.grid = []
        for row in map_definition:
            grid_row = []
            for char in row:
                if char == 'F':
                    grid_row.append(TileType.FLOOR)
                elif char == 'W':
                    grid_row.append(TileType.WALL)
                elif char == 'K':
                    grid_row.append(TileType.KEY)
                elif char == 'D':
                    grid_row.append(TileType.DOOR)
                elif char == 'E':
                    grid_row.append(TileType.EXIT)
                else:
                    grid_row.append(TileType.FLOOR)
            self.grid.append(grid_row)
        
        # 设置机器人初始状态
        self.bot_x, self.bot_y = bot_start
        self.bot_direction = bot_direction
        self.keys_collected = 0
        self.doors_opened = 0
        
        # 返回机器人初始状态
        bot_state = {
            'x': self.bot_x,
            'y': self.bot_y,
            'direction': self.bot_direction,
            'have_key': False,
            'has_open_door': False
        }
        
        return self, bot_state
    
    def getTile(self, x: int, y: int) -> Optional[TileType]:
        """获取指定位置的瓦片类型"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def getBotPosition(self) -> Tuple[int, int]:
        """获取机器人当前位置"""
        return (self.bot_x, self.bot_y)
    
    def getBotDirection(self) -> str:
        """获取机器人当前朝向"""
        return self.bot_direction
    
    def isWall(self, x: int, y: int) -> bool:
        """检查指定位置是否为墙"""
        tile = self.getTile(x, y)
        return tile == TileType.WALL
    
    def isKey(self, x: int, y: int) -> bool:
        """检查指定位置是否有钥匙"""
        tile = self.getTile(x, y)
        return tile == TileType.KEY
    
    def isDoor(self, x: int, y: int) -> bool:
        """检查指定位置是否为门"""
        tile = self.getTile(x, y)
        return tile == TileType.DOOR
    
    def isExit(self, x: int, y: int) -> bool:
        """检查指定位置是否为出口"""
        tile = self.getTile(x, y)
        return tile == TileType.EXIT
    
    def isFloor(self, x: int, y: int) -> bool:
        """检查指定位置是否为地板"""
        tile = self.getTile(x, y)
        return tile == TileType.FLOOR
    
    def removeKey(self, x: int, y: int) -> bool:
        """移除指定位置的钥匙"""
        if self.isKey(x, y):
            self.grid[y][x] = TileType.FLOOR
            return True
        return False
    
    def openDoor(self, x: int, y: int) -> bool:
        """打开指定位置的门"""
        if self.isDoor(x, y):
            self.grid[y][x] = TileType.FLOOR
            return True
        return False
    
    def getFrontTile(self, bot_x: int, bot_y: int, direction: str) -> Optional[TileType]:
        """获取机器人前方的瓦片类型"""
        front_x, front_y = self.getFrontPosition(bot_x, bot_y, direction)
        return self.getTile(front_x, front_y)
    
    def getFrontPosition(self, bot_x: int, bot_y: int, direction: str) -> Tuple[int, int]:
        """获取机器人前方的位置坐标"""
        if direction == "N":
            return (bot_x, bot_y - 1)
        elif direction == "E":
            return (bot_x + 1, bot_y)
        elif direction == "S":
            return (bot_x, bot_y + 1)
        elif direction == "W":
            return (bot_x - 1, bot_y)
        else:
            return (bot_x, bot_y)
    
    def isFrontClear(self, bot_x: int, bot_y: int, direction: str) -> bool:
        """检查机器人前方是否清晰（不是墙）"""
        front_tile = self.getFrontTile(bot_x, bot_y, direction)
        return front_tile != TileType.WALL
    
    def updateBot(self, new_x: int, new_y: int, new_direction: str):
        """更新机器人状态"""
        self.bot_x = new_x
        self.bot_y = new_y
        self.bot_direction = new_direction
    
    def updateKey(self, x: int, y: int):
        """更新钥匙状态（移除）"""
        self.removeKey(x, y)
        self.keys_collected += 1
    
    def updateDoor(self, x: int, y: int):
        """更新门状态（打开）"""
        self.openDoor(x, y)
        self.doors_opened += 1
    
    def printWorld(self):
        """打印当前世界状态（用于调试）"""
        print(f"World ({self.width}x{self.height})")
        print(f"Bot at ({self.bot_x}, {self.bot_y}) facing {self.bot_direction}")
        print(f"Keys collected: {self.keys_collected}")
        print(f"Doors opened: {self.doors_opened}")
        
        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                if x == self.bot_x and y == self.bot_y:
                    # 显示机器人位置和朝向
                    if self.bot_direction == "N":
                        row_str += "↑"
                    elif self.bot_direction == "E":
                        row_str += "→"
                    elif self.bot_direction == "S":
                        row_str += "↓"
                    elif self.bot_direction == "W":
                        row_str += "←"
                else:
                    tile = self.grid[y][x]
                    if tile == TileType.FLOOR:
                        row_str += "."
                    elif tile == TileType.WALL:
                        row_str += "#"
                    elif tile == TileType.KEY:
                        row_str += "K"
                    elif tile == TileType.DOOR:
                        row_str += "D"
                    elif tile == TileType.EXIT:
                        row_str += "E"
            print(row_str)
        print()


# 预定义的地图模板
def createSimpleCorridor() -> List[List[str]]:
    """创建简单走廊地图"""
    return [
        "WWWWWWWWWW",
        "W........W",
        "W........W",
        "W........W",
        "W........W",
        "W........W",
        "W........W",
        "W........W",
        "W.......EW",
        "WWWWWWWWWW"
    ]

def createCorridorWithTurn() -> List[List[str]]:
    """创建有转弯的走廊地图"""
    return [
        "WWWWWWWWWW",
        "W........W",
        "W........W",
        "W........W",
        "W....WWWWW",
        "W....W...W",
        "W....W...W",
        "W....W...W",
        "W...EW...W",
        "WWWWWWWWWW"
    ]

def createRoomWithKeyAndDoor() -> List[List[str]]:
    """创建包含钥匙和门的房间地图"""
    return [
        "WWWWWWWWWW",
        "W........W",
        "W.K......W",
        "W........W",
        "W....D...W",
        "W........W",
        "W........W",
        "W........W",
        "W........W",
        "WWWWWWWWWE"
    ]

def createComplexMaze() -> List[List[str]]:
    """创建复杂迷宫地图"""
    return [
        "WWWWWWWWWW",
        "W.K.....WW",
        "W.WWWW..WW",
        "W.WWWW..WW",
        "W.WWWW..WW",
        "W.WWWW..WW",
        "W.WWWW..WW",
        "W.WWWW..WW",
        "W....D..WW",
        "WWWWWWWWWE"
    ] 