"""
Robot Module

Implements basic robot functionality including movement, turning, sensor detection, and action execution.
The robot can only see one cell ahead and must use sensors to understand the environment.
"""

from typing import Tuple, Optional
from world import World, TileType


class Bot:
    """Robot class"""
    
    def __init__(self, world: World, x: int, y: int, direction: str = "N"):
        """
        Initialize robot
        
        Args:
            world: World object
            x: Initial x coordinate
            y: Initial y coordinate
            direction: Initial direction (N, E, S, W)
        """
        self.world = world
        self.x = x
        self.y = y
        self.direction = direction
        self.have_key = False
        self.has_open_door = False
        self.steps_taken = 0
        self.max_steps = 1000  # Prevent infinite loops
        
    def get_pose(self) -> Tuple[int, int]:
        """Get robot's current position"""
        return (self.x, self.y)
    
    def get_direction(self) -> str:
        """Get robot's current direction"""
        return self.direction
    
    def is_on_key(self) -> bool:
        """Check if robot is on a key"""
        return self.world.isKey(self.x, self.y)
    
    def is_on_door(self) -> bool:
        """Check if robot is on a door"""
        return self.world.isDoor(self.x, self.y)
    
    def is_on_exit(self) -> bool:
        """Check if robot is at exit"""
        return self.world.isExit(self.x, self.y)
    
    def front_is_clear(self) -> bool:
        """Check if robot's front is clear (not a wall)"""
        return self.world.isFrontClear(self.x, self.y, self.direction)
    
    def at_key(self) -> bool:
        """Check if robot is at key location (alias)"""
        return self.is_on_key()
    
    def at_door(self) -> bool:
        """Check if robot is at door location (alias)"""
        return self.is_on_door()
    
    def at_exit(self) -> bool:
        """Check if robot is at exit location (alias)"""
        return self.is_on_exit()
    
    def move_forward(self) -> bool:
        """
        Move forward one cell
        
        Returns:
            bool: Whether movement was successful
        """
        if self.steps_taken >= self.max_steps:
            raise RuntimeError("Robot movement steps exceeded limit")
            
        if not self.front_is_clear():
            return False  # Wall ahead, cannot move
            
        # Calculate new position
        new_x, new_y = self.world.getFrontPosition(self.x, self.y, self.direction)
        
        # Update position
        old_x, old_y = self.x, self.y
        self.x, self.y = new_x, new_y
        
        # Update world state
        self.world.updateBot(self.x, self.y, self.direction)
        
        self.steps_taken += 1
        return True
    
    def turn_left(self) -> None:
        """Turn left"""
        if self.direction == "N":
            self.direction = "W"
        elif self.direction == "W":
            self.direction = "S"
        elif self.direction == "S":
            self.direction = "E"
        elif self.direction == "E":
            self.direction = "N"
        
        # update world state
        self.world.updateBot(self.x, self.y, self.direction)
    
    def turn_right(self) -> None:
        """Turn right"""
        if self.direction == "N":
            self.direction = "E"
        elif self.direction == "E":
            self.direction = "S"
        elif self.direction == "S":
            self.direction = "W"
        elif self.direction == "W":
            self.direction = "N"
        
        # update world state
        self.world.updateBot(self.x, self.y, self.direction)
    
    def pick_key(self) -> bool:
        """
        Pick up key at current cell
        
        Returns:
            bool: Whether pickup was successful
        """
        if self.is_on_key():
            self.world.updateKey(self.x, self.y)
            self.have_key = True
            return True
        return False
    
    def open_door(self) -> bool:
        """
        Open door
        
        Returns:
            bool: Whether door opening was successful
        """
        if self.is_on_door() and self.have_key:
            self.world.updateDoor(self.x, self.y)
            self.has_open_door = True
            return True
        return False
    
    def look(self) -> Optional[TileType]:
        """
        Look at tile type one cell ahead
        
        Returns:
            TileType: Tile type ahead, returns None if out of bounds
        """
        return self.world.getFrontTile(self.x, self.y, self.direction)
    
    def get_status(self) -> dict:
        """Get robot's current status"""
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
        """Reset robot state"""
        self.x = x
        self.y = y
        self.direction = direction
        self.have_key = False
        self.has_open_door = False
        self.steps_taken = 0
        self.world.updateBot(self.x, self.y, self.direction)
    
    def can_exit(self) -> bool:
        """Check if robot can exit (at exit location)"""
        return self.is_on_exit()
    
    def exit(self) -> bool:
        """
        Exit the world
        
        Returns:
            bool: Whether exit was successful
        """
        if self.can_exit():
            return True
        return False
    
    def get_front_position(self) -> Tuple[int, int]:
        """Get position coordinates in front of robot"""
        return self.world.getFrontPosition(self.x, self.y, self.direction)
    
    def get_front_tile(self) -> Optional[TileType]:
        """Get tile type in front of robot"""
        return self.world.getFrontTile(self.x, self.y, self.direction)
    
    def is_stuck(self) -> bool:
        """Check if robot is stuck (cannot move)"""
        # Check if all four directions are blocked by walls
        directions = ["N", "E", "S", "W"]
        for direction in directions:
            if self.world.isFrontClear(self.x, self.y, direction):
                return False
        return True
    
    def get_available_moves(self) -> list:
        """Get available movement directions"""
        available = []
        directions = ["N", "E", "S", "W"]
        for direction in directions:
            if self.world.isFrontClear(self.x, self.y, direction):
                available.append(direction)
        return available 