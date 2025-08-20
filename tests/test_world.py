"""
Vault Runner 测试模块

包含5个自动化测试用例，测试世界模型、机器人和解释器的基本功能。
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world import World, createSimpleCorridor, createCorridorWithTurn, createRoomWithKeyAndDoor
from bot import Bot
from interpreter import Interpreter, Tokenizer, Parser


class TestWorld(unittest.TestCase):
    """世界模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.world = World()
    
    def test_simple_corridor_creation(self):
        """测试1: 简单走廊到出口"""
        map_def = createSimpleCorridor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # 验证世界尺寸
        self.assertEqual(world.width, 10)
        self.assertEqual(world.height, 10)
        
        # 验证机器人初始位置
        self.assertEqual(world.getBotPosition(), (1, 1))
        self.assertEqual(world.getBotDirection(), "S")
        
        # 验证出口位置
        self.assertTrue(world.isExit(9, 9))
        
        # 验证起始位置是地板
        self.assertTrue(world.isFloor(1, 1))
        
        # 验证墙壁位置
        self.assertTrue(world.isWall(0, 0))
        self.assertTrue(world.isWall(9, 0))
    
    def test_corridor_with_turn(self):
        """测试2: 有转弯的走廊"""
        map_def = createCorridorWithTurn()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # 验证转弯处的墙壁
        self.assertTrue(world.isWall(4, 4))
        self.assertTrue(world.isWall(5, 4))
        self.assertTrue(world.isWall(6, 4))
        self.assertTrue(world.isWall(7, 4))
        self.assertTrue(world.isWall(8, 4))
        
        # 验证转弯后的通道
        self.assertTrue(world.isFloor(4, 5))
        self.assertTrue(world.isFloor(4, 6))
        self.assertTrue(world.isFloor(4, 7))
        self.assertTrue(world.isFloor(4, 8))
        
        # 验证出口位置
        self.assertTrue(world.isExit(9, 9))
    
    def test_room_with_key_and_door(self):
        """测试3: 简单房间：钥匙在门前"""
        map_def = createRoomWithKeyAndDoor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # 验证钥匙位置
        self.assertTrue(world.isKey(2, 2))
        
        # 验证门位置
        self.assertTrue(world.isDoor(5, 4))
        
        # 验证出口位置
        self.assertTrue(world.isExit(9, 9))
        
        # 验证钥匙和门之间的路径
        self.assertTrue(world.isFloor(3, 2))
        self.assertTrue(world.isFloor(4, 2))
        self.assertTrue(world.isFloor(5, 2))
        self.assertTrue(world.isFloor(5, 3))
    
    def test_door_blocking_exit(self):
        """测试4: 门阻挡出口：需要钥匙开门"""
        map_def = createRoomWithKeyAndDoor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        
        # 机器人应该能够拾取钥匙
        bot = Bot(world, 1, 1, "S")
        
        # 移动到钥匙位置
        bot.turn_right()  # 转向东
        bot.move_forward()  # 移动到(2,1)
        bot.turn_left()   # 转向北
        bot.move_forward()  # 移动到(2,2) - 钥匙位置
        
        self.assertTrue(bot.is_on_key())
        
        # 拾取钥匙
        self.assertTrue(bot.pick_key())
        self.assertTrue(bot.have_key)
        
        # 移动到门位置
        bot.turn_right()  # 转向东
        for _ in range(3):
            bot.move_forward()  # 移动到(5,2)
        bot.turn_left()   # 转向北
        for _ in range(2):
            bot.move_forward()  # 移动到(5,4) - 门位置
        
        self.assertTrue(bot.is_on_door())
        
        # 开门
        self.assertTrue(bot.open_door())
        self.assertTrue(bot.has_open_door)
        
        # 门应该被移除
        self.assertFalse(world.isDoor(5, 4))
        self.assertTrue(world.isFloor(5, 4))
    
    def test_bot_cannot_move_through_wall(self):
        """测试5: 失败情况：前方为墙时move()不得穿墙"""
        map_def = createSimpleCorridor()
        world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        bot = Bot(world, 1, 1, "S")
        
        # 机器人面向南，前方是地板，可以移动
        self.assertTrue(bot.front_is_clear())
        self.assertTrue(bot.move_forward())
        self.assertEqual(bot.get_pose(), (1, 2))
        
        # 机器人面向北，前方是墙，不能移动
        bot.turn_left()
        bot.turn_left()  # 现在面向北
        self.assertFalse(bot.front_is_clear())
        self.assertFalse(bot.move_forward())
        self.assertEqual(bot.get_pose(), (1, 2))  # 位置不变


class TestBot(unittest.TestCase):
    """机器人测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.world = World()
        map_def = createSimpleCorridor()
        self.world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        self.bot = Bot(self.world, 1, 1, "S")
    
    def test_bot_movement(self):
        """测试机器人移动功能"""
        # 测试向前移动
        initial_pos = self.bot.get_pose()
        self.assertTrue(self.bot.move_forward())
        new_pos = self.bot.get_pose()
        self.assertNotEqual(initial_pos, new_pos)
        
        # 测试转向
        initial_direction = self.bot.get_direction()
        self.bot.turn_left()
        self.assertNotEqual(initial_direction, self.bot.get_direction())
        
        self.bot.turn_right()
        self.assertEqual(initial_direction, self.bot.get_direction())
    
    def test_bot_sensors(self):
        """测试机器人传感器"""
        # 测试前方是否清晰
        self.assertTrue(self.bot.front_is_clear())
        
        # 测试是否在钥匙上
        self.assertFalse(self.bot.is_on_key())
        
        # 测试是否在门上
        self.assertFalse(self.bot.is_on_door())
        
        # 测试是否在出口
        self.assertFalse(self.bot.is_on_exit())
    
    def test_bot_actions(self):
        """测试机器人动作"""
        # 测试拾取钥匙（当前位置没有钥匙）
        self.assertFalse(self.bot.pick_key())
        self.assertFalse(self.bot.have_key)
        
        # 测试开门（当前位置没有门，也没有钥匙）
        self.assertFalse(self.bot.open_door())
        self.assertFalse(self.bot.has_open_door)


class TestInterpreter(unittest.TestCase):
    """解释器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.world = World()
        map_def = createSimpleCorridor()
        self.world, bot_state = self.world.setWorld(map_def, (1, 1), "S")
        self.bot = Bot(self.world, 1, 1, "S")
        self.interpreter = Interpreter(self.world, self.bot)
    
    def test_tokenizer(self):
        """测试词法分析器"""
        source = "MOVE LEFT RIGHT"
        tokens = self.interpreter.tokenizer.tokenize(source)
        
        # 过滤掉空白和EOF token
        meaningful_tokens = [t for t in tokens if t.type.value not in ['WHITESPACE', 'EOF']]
        self.assertEqual(len(meaningful_tokens), 3)
        self.assertEqual(meaningful_tokens[0].type, self.interpreter.tokenizer.keywords['MOVE'])
        self.assertEqual(meaningful_tokens[1].type, self.interpreter.tokenizer.keywords['LEFT'])
        self.assertEqual(meaningful_tokens[2].type, self.interpreter.tokenizer.keywords['RIGHT'])
    
    def test_simple_program_execution(self):
        """测试简单程序执行"""
        source = """MOVE
LEFT
MOVE"""
        
        success = self.interpreter.run(source)
        # 程序应该执行成功，但不一定到达出口
        self.assertIsInstance(success, bool)
    
    def test_constraint_enforcement(self):
        """测试约束执行"""
        # 测试嵌套深度限制
        deep_nested_source = """IF FRONT_CLEAR:
  IF FRONT_CLEAR:
    IF FRONT_CLEAR:
      IF FRONT_CLEAR:
        MOVE
      ENDIF
    ENDIF
  ENDIF
ENDIF"""
        
        # 应该抛出嵌套深度超限异常
        with self.assertRaises(Exception):
            self.interpreter.run(deep_nested_source)
        
        # 测试循环上限
        large_loop_source = "LOOP 100 TIMES: MOVE ENDLOOP"
        
        # 应该抛出循环上限超限异常
        with self.assertRaises(Exception):
            self.interpreter.run(large_loop_source)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2) 