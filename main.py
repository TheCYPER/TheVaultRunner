#!/usr/bin/env python3
"""
Vault Runner 主程序

支持运行示例程序和文件，提供命令行接口。
"""

import sys
import os
import argparse
from pathlib import Path
from world import World, createSimpleCorridor, createCorridorWithTurn, createRoomWithKeyAndDoor
from bot import Bot
from interpreter import Interpreter


def load_program(file_path: str) -> str:
    """
    从文件加载程序源代码
    
    Args:
        file_path: 程序文件路径
        
    Returns:
        str: 程序源代码
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败: {e}")
        sys.exit(1)


def run_program(program_source: str, world_map: list, bot_start: tuple, bot_direction: str = "N", verbose: bool = False) -> bool:
    """
    运行程序
    
    Args:
        program_source: 程序源代码
        world_map: 世界地图定义
        bot_start: 机器人起始位置
        bot_direction: 机器人起始朝向
        verbose: 是否详细输出
        
    Returns:
        bool: 程序是否成功执行
    """
    # 创建世界
    world = World()
    world, bot_state = world.setWorld(world_map, bot_start, bot_direction)
    
    # 创建机器人
    bot = Bot(world, bot_state['x'], bot_state['y'], bot_state['direction'])
    
    # 创建解释器
    interpreter = Interpreter(world, bot)
    
    if verbose:
        print("初始世界状态:")
        world.printWorld()
        print(f"机器人起始位置: ({bot_start[0]}, {bot_start[1]}) 朝向: {bot_direction}")
        print(f"程序Token数量: {interpreter.get_token_count(program_source)}")
        print("\n开始执行程序...\n")
    
    # 运行程序
    success = interpreter.run(program_source)
    
    if verbose:
        print("\n最终世界状态:")
        world.printWorld()
        print(f"机器人最终位置: {bot.get_pose()}")
        print(f"机器人朝向: {bot.get_direction()}")
        print(f"是否持有钥匙: {bot.have_key}")
        print(f"是否成功到达出口: {success}")
    
    return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Vault Runner - 迷你编程语言解释器")
    parser.add_argument("program", nargs="?", help="程序文件路径或示例名称")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--list-examples", action="store_true", help="列出可用示例")
    
    args = parser.parse_args()
    
    # 预定义的示例程序
    examples = {
        "corridor": {
            "source": """LOOP 50:
  IF AT_EXIT:
    END
  ENDIF
  IF FRONT_CLEAR:
    MOVE
  ELSE:
    RIGHT
  ENDIF
ENDLOOP""",
            "map": createSimpleCorridor(),
            "start": (1, 1),
            "direction": "E",
            "description": "简单走廊导航 - 右侧优先墙跟随策略"
        },
        "corridor_turn": {
            "source": """LOOP 50:
  IF FRONT_CLEAR:
    MOVE
  ELSE:
    RIGHT
  ENDIF
ENDLOOP""",
            "map": createCorridorWithTurn(),
            "start": (1, 1),
            "direction": "S",
            "description": "有转弯的走廊导航"
        },
        "collect_and_open": {
            "source": """LOOP 50:
  IF ON_KEY:
    PICK
  ENDIF
  IF AT_DOOR AND HAVE_KEY:
    OPEN
  ENDIF
  IF FRONT_CLEAR:
    MOVE
  ELSE:
    RIGHT
  ENDIF
  IF AT_EXIT:
    END
  ENDIF
ENDLOOP""",
            "map": createRoomWithKeyAndDoor(),
            "start": (1, 1),
            "direction": "S",
            "description": "收集钥匙并开门，然后到达出口"
        }
    }
    
    if args.list_examples:
        print("可用的示例程序:")
        for name, example in examples.items():
            print(f"  {name}: {example['description']}")
        return
    
    if not args.program:
        print("Vault Runner - 迷你编程语言解释器")
        print("用法:")
        print("  python main.py <程序文件>")
        print("  python main.py <示例名称>")
        print("  python main.py --list-examples")
        print("\n示例:")
        print("  python main.py corridor")
        print("  python main.py examples/collect_and_open.runner")
        return
    
    # 检查是否为预定义示例
    if args.program in examples:
        example = examples[args.program]
        print(f"运行示例: {args.program}")
        print(f"描述: {example['description']}")
        print(f"Token数量: {len(example['source'].split())}")
        print()
        
        success = run_program(
            example['source'],
            example['map'],
            example['start'],
            example['direction'],
            args.verbose
        )
        
        if success:
            print(f"\n✅ 示例 {args.program} 执行成功!")
        else:
            print(f"\n❌ 示例 {args.program} 执行失败!")
    
    else:
        # 从文件加载程序
        if not os.path.exists(args.program):
            print(f"错误: 找不到程序文件 {args.program}")
            print("可用的示例: " + ", ".join(examples.keys()))
            return
        
        print(f"运行程序文件: {args.program}")
        
        # 根据文件名选择合适的地图
        if "corridor" in args.program.lower():
            world_map = createSimpleCorridor()
            bot_start = (1, 1)
            bot_direction = "S"
        elif "key" in args.program.lower() or "door" in args.program.lower():
            world_map = createRoomWithKeyAndDoor()
            bot_start = (1, 1)
            bot_direction = "S"
        else:
            world_map = createSimpleCorridor()
            bot_start = (1, 1)
            bot_direction = "S"
        
        program_source = load_program(args.program)
        
        success = run_program(
            program_source,
            world_map,
            bot_start,
            bot_direction,
            args.verbose
        )
        
        if success:
            print(f"\n✅ 程序 {args.program} 执行成功!")
        else:
            print(f"\n❌ 程序 {args.program} 执行失败!")


if __name__ == "__main__":
    main() 