"""
World Model Module

Implements 2D grid world containing floors, walls, keys, doors, and exits.
Manages world state and robot position updates.
"""

from typing import List, Tuple, Optional
from enum import Enum


class TileType(Enum):
    """Tile type enumeration"""
    FLOOR = "FLOOR"      # Floor
    WALL = "WALL"        # Wall
    KEY = "KEY"          # Key
    DOOR = "DOOR"        # Door
    EXIT = "EXIT"        # Exit


class World:
    """2D grid world class"""
    
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
        Initialize world map and robot initial state
        
        Args:
            map_definition: List of strings, each string represents a map row
            bot_start: Robot starting position (x, y)
            bot_direction: Robot initial direction
            
        Returns:
            (world, bot_state): World object and robot initial state
        """
        self.height = len(map_definition)
        self.width = len(map_definition[0]) if map_definition else 0
        
        # Initialize grid
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
        
        # Set robot initial state
        self.bot_x, self.bot_y = bot_start
        self.bot_direction = bot_direction
        self.keys_collected = 0
        self.doors_opened = 0
        
        # Return robot initial state
        bot_state = {
            'x': self.bot_x,
            'y': self.bot_y,
            'direction': self.bot_direction,
            'have_key': False,
            'has_open_door': False
        }
        
        return self, bot_state
    
    def getTile(self, x: int, y: int) -> Optional[TileType]:
        """Get tile type at specified position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def getBotPosition(self) -> Tuple[int, int]:
        """Get robot's current position"""
        return (self.bot_x, self.bot_y)
    
    def getBotDirection(self) -> str:
        """Get robot's current direction"""
        return self.bot_direction
    
    def isWall(self, x: int, y: int) -> bool:
        """Check if specified position is a wall"""
        tile = self.getTile(x, y)
        return tile == TileType.WALL
    
    def isKey(self, x: int, y: int) -> bool:
        """Check if specified position has a key"""
        tile = self.getTile(x, y)
        return tile == TileType.KEY
    
    def isDoor(self, x: int, y: int) -> bool:
        """Check if specified position is a door"""
        tile = self.getTile(x, y)
        return tile == TileType.DOOR
    
    def isExit(self, x: int, y: int) -> bool:
        """Check if specified position is an exit"""
        tile = self.getTile(x, y)
        return tile == TileType.EXIT
    
    def isFloor(self, x: int, y: int) -> bool:
        """Check if specified position is a floor"""
        tile = self.getTile(x, y)
        return tile == TileType.FLOOR
    
    def removeKey(self, x: int, y: int) -> bool:
        """Remove key at specified position"""
        if self.isKey(x, y):
            self.grid[y][x] = TileType.FLOOR
            return True
        return False
    
    def openDoor(self, x: int, y: int) -> bool:
        """Open door at specified position"""
        if self.isDoor(x, y):
            self.grid[y][x] = TileType.FLOOR
            return True
        return False
    
    def getFrontTile(self, bot_x: int, bot_y: int, direction: str) -> Optional[TileType]:
        """Get tile type in front of robot"""
        front_x, front_y = self.getFrontPosition(bot_x, bot_y, direction)
        return self.getTile(front_x, front_y)
    
    def getFrontPosition(self, bot_x: int, bot_y: int, direction: str) -> Tuple[int, int]:
        """Get position coordinates in front of robot"""
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
        """Check if robot's front is not a wall"""
        front_tile = self.getFrontTile(bot_x, bot_y, direction)
        return front_tile != TileType.WALL
    
    def updateBot(self, new_x: int, new_y: int, new_direction: str):
        """Update robot state"""
        self.bot_x = new_x
        self.bot_y = new_y
        self.bot_direction = new_direction
    
    def updateKey(self, x: int, y: int):
        """Update key state (remove)"""
        self.removeKey(x, y)
        self.keys_collected += 1
    
    def updateDoor(self, x: int, y: int):
        """Update door state (open)"""
        self.openDoor(x, y)
        self.doors_opened += 1
    
    def printWorld(self):
        """Print current world state (for debugging)"""
        print(f"World ({self.width}x{self.height})")
        print(f"Bot at ({self.bot_x}, {self.bot_y}) facing {self.bot_direction}")
        print(f"Keys collected: {self.keys_collected}")
        print(f"Doors opened: {self.doors_opened}")
        
        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                if x == self.bot_x and y == self.bot_y:
                    # Show robot position and direction
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


# Predefined map templates
def createSimpleCorridor() -> List[List[str]]:
    """Create simple corridor map"""
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
    """Create corridor map with turns"""
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
    """Create room map with keys and doors"""
    return [
        "WWWWWWWWWW",
        "W..K.....W",
        "W........W",
        "W.......DW",
        "W........W",
        "W........W",
        "W........W",
        "W........W",
        "W.......EW",
        "WWWWWWWWWW"
    ]

def createComplexMaze() -> List[List[str]]:
    """Create complex maze map"""
    return [
        "WWWWWWWWWW",
        "W.K......W",
        "W.WWWW...W",
        "W.WDWW...W",
        "W.W..W...W",
        "W.WW.W...W",
        "W.WW.W...W",
        "W.WW.W...W",
        "W......E.W",
        "WWWWWWWWWW"
    ] 