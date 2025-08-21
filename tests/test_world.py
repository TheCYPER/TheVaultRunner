"""
Vault Runner Test Module

Contains 5 automated test cases testing basic functionality of world model, robot, and interpreter.
"""

import sys
import os
import unittest

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world import World, createSimpleCorridor, createCorridorWithTurn, createRoomWithKeyAndDoor
from bot import Bot
from interpreter import Interpreter, Tokenizer, Parser


class TestWorld(unittest.TestCase):
    """World model test class"""
    
    def setUp(self):
        """Test preparation"""
        self.world = World()
    
    def test_simple_corridor_creation(self):
        """Test 1: Simple corridor to exit"""
        map_def = createSimpleCorridor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # Verify world dimensions
        self.assertEqual(world.width, 10)
        self.assertEqual(world.height, 10)
        
        # Verify robot initial position
        self.assertEqual(world.getBotPosition(), (1, 1))
        self.assertEqual(world.getBotDirection(), "S")
        
        # Verify exit position
        self.assertTrue(world.isExit(9, 9))
        
        # Verify starting position is floor
        self.assertTrue(world.isFloor(1, 1))
        
        # Verify wall positions
        self.assertTrue(world.isWall(0, 0))
        self.assertTrue(world.isWall(9, 0))
    
    def test_corridor_with_turn(self):
        """Test 2: Corridor with turns"""
        map_def = createCorridorWithTurn()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # Verify walls at turn
        self.assertTrue(world.isWall(4, 4))
        self.assertTrue(world.isWall(5, 4))
        self.assertTrue(world.isWall(6, 4))
        self.assertTrue(world.isWall(7, 4))
        self.assertTrue(world.isWall(8, 4))
        
        # Verify passage after turn
        self.assertTrue(world.isFloor(4, 5))
        self.assertTrue(world.isFloor(4, 6))
        self.assertTrue(world.isFloor(4, 7))
        self.assertTrue(world.isFloor(4, 8))
        
        # Verify exit position
        self.assertTrue(world.isExit(9, 9))
    
    def test_room_with_key_and_door(self):
        """Test 3: Simple room: key in front of door"""
        map_def = createRoomWithKeyAndDoor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # Verify key position
        self.assertTrue(world.isKey(2, 2))
        
        # Verify door position
        self.assertTrue(world.isDoor(5, 4))
        
        # Verify exit position
        self.assertTrue(world.isExit(9, 9))
        
        # Verify path between key and door
        self.assertTrue(world.isFloor(3, 2))
        self.assertTrue(world.isFloor(4, 2))
        self.assertTrue(world.isFloor(5, 2))
        self.assertTrue(world.isFloor(5, 3))
    
    def test_door_blocking_exit(self):
        """Test 4: Door blocking exit: needs key to open door"""
        map_def = createRoomWithKeyAndDoor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # Robot should be able to pick up key
        bot = Bot(world, 1, 1, "S")
        
        # Move to key position
        bot.turn_right()  # Turn east
        bot.move_forward()  # Move to (2,1)
        bot.turn_left()   # Turn north
        bot.move_forward()  # Move to (2,2) - key position
        
        self.assertTrue(bot.is_on_key())
        
        # Pick up key
        self.assertTrue(bot.pick_key())
        self.assertTrue(bot.have_key)
        
        # Move to door position
        bot.turn_right()  # Turn east
        for _ in range(3):
            bot.move_forward()  # Move to (5,2)
        bot.turn_left()   # Turn north
        for _ in range(2):
            bot.move_forward()  # Move to (5,4) - door position
        
        self.assertTrue(bot.is_on_door())
        
        # Open door
        self.assertTrue(bot.open_door())
        self.assertTrue(bot.has_open_door)
        
        # Door should be removed
        self.assertFalse(world.isDoor(5, 4))
        self.assertTrue(world.isFloor(5, 4))
    
    def test_bot_cannot_move_through_wall(self):
        """Test 5: Failure case: move() should not pass through wall when front is wall"""
        map_def = createSimpleCorridor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        bot = Bot(world, 1, 1, "S")
        
        # Robot facing south, front is floor, can move
        self.assertTrue(bot.front_is_clear())
        self.assertTrue(bot.move_forward())
        self.assertEqual(bot.get_pose(), (1, 2))
        
        # Robot facing north, front is wall, cannot move
        bot.turn_left()
        bot.turn_left()  # Now facing north
        self.assertFalse(bot.front_is_clear())
        self.assertFalse(bot.move_forward())
        self.assertEqual(bot.get_pose(), (1, 2))  # Position unchanged


class TestBot(unittest.TestCase):
    """Robot test class"""
    
    def setUp(self):
        """Test preparation"""
        self.world = World()
        map_def = createSimpleCorridor()
        self.world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        self.bot = Bot(self.world, 1, 1, "S")
    
    def test_bot_movement(self):
        """Test robot movement functionality"""
        # Test forward movement
        initial_pos = self.bot.get_pose()
        self.assertTrue(self.bot.move_forward())
        new_pos = self.bot.get_pose()
        self.assertNotEqual(initial_pos, new_pos)
        
        # Test turning
        initial_direction = self.bot.get_direction()
        self.bot.turn_left()
        self.assertNotEqual(initial_direction, self.bot.get_direction())
        
        self.bot.turn_right()
        self.assertEqual(initial_direction, self.bot.get_direction())
    
    def test_bot_sensors(self):
        """Test robot sensors"""
        # Test if front is clear
        self.assertTrue(self.bot.front_is_clear())
        
        # Test if on key
        self.assertFalse(self.bot.is_on_key())
        
        # Test if on door
        self.assertFalse(self.bot.is_on_door())
        
        # Test if at exit
        self.assertFalse(self.bot.is_on_exit())
    
    def test_bot_actions(self):
        """Test robot actions"""
        # Test picking up key (no key at current position)
        self.assertFalse(self.bot.pick_key())
        self.assertFalse(self.bot.have_key)
        
        # Test opening door (no door at current position, no key either)
        self.assertFalse(self.bot.open_door())
        self.assertFalse(self.bot.has_open_door)


class TestInterpreter(unittest.TestCase):
    """Interpreter test class"""
    
    def setUp(self):
        """Test preparation"""
        self.world = World()
        map_def = createSimpleCorridor()
        self.world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        self.bot = Bot(self.world, 1, 1, "S")
        self.interpreter = Interpreter(self.world, self.bot)
    
    def test_tokenizer(self):
        """Test lexical analyzer"""
        source = "MOVE LEFT RIGHT"
        tokens = self.interpreter.tokenizer.tokenize(source)
        
        # Filter out whitespace and EOF tokens
        meaningful_tokens = [t for t in tokens if t.type.value not in ['WHITESPACE', 'EOF']]
        self.assertEqual(len(meaningful_tokens), 3)
        self.assertEqual(meaningful_tokens[0].type, self.interpreter.tokenizer.keywords['MOVE'])
        self.assertEqual(meaningful_tokens[1].type, self.interpreter.tokenizer.keywords['LEFT'])
        self.assertEqual(meaningful_tokens[2].type, self.interpreter.tokenizer.keywords['RIGHT'])
    
    def test_simple_program_execution(self):
        """Test simple program execution"""
        source = """MOVE
LEFT
MOVE"""
        
        success = self.interpreter.run(source)
        # Program should execute successfully, but may not reach exit
        self.assertIsInstance(success, bool)
    
    def test_constraint_enforcement(self):
        """Test constraint enforcement"""
        # Test nesting depth limit
        deep_nested_source = """IF FRONT_CLEAR:
  IF FRONT_CLEAR:
    IF FRONT_CLEAR:
      IF FRONT_CLEAR:
        MOVE
      ENDIF
    ENDIF
  ENDIF
ENDIF"""
        
        # Should raise nesting depth exceeded exception
        with self.assertRaises(Exception):
            self.interpreter.run(deep_nested_source)
        
        # Test loop limit
        large_loop_source = "LOOP 100 TIMES: MOVE ENDLOOP"
        
        # Should raise loop limit exceeded exception
        with self.assertRaises(Exception):
            self.interpreter.run(large_loop_source)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 