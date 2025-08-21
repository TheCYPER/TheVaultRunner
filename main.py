#!/usr/bin/env python3
"""
Vault Runner Main Program

Supports running example programs and files, provides command line interface.
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
    Load program source code from file
    
    Args:
        file_path: Program file path
        
    Returns:
        str: Program source code
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read file: {e}")
        sys.exit(1)


def run_program(program_source: str, world_map: list, bot_start: tuple, bot_direction: str = "N", verbose: bool = False) -> bool:
    """
    Run program
    
    Args:
        program_source: Program source code
        world_map: World map definition
        bot_start: Robot starting position
        bot_direction: Robot starting direction
        verbose: Whether to output detailed information
        
    Returns:
        bool: Whether the program executed successfully
    """
    # Create world
    world = World()
    world, bot_state = world.setWorld(world_map, bot_start, bot_direction)
    
    # Create robot
    bot = Bot(world, bot_state['x'], bot_state['y'], bot_state['direction'])
    
    # Create interpreter
    interpreter = Interpreter(world, bot)
    
    if verbose:
        print("Initial world state:")
        world.printWorld()
        print(f"Robot starting position: ({bot_start[0]}, {bot_start[1]}) Direction: {bot_direction}")
        print(f"Program token count: {interpreter.get_token_count(program_source)}")
        print("\nStarting program execution...\n")
    
    # Run program
    success = interpreter.run(program_source)
    
    if verbose:
        print("\nFinal world state:")
        world.printWorld()
        print(f"Robot final position: {bot.get_pose()}")
        print(f"Robot direction: {bot.get_direction()}")
        print(f"Has key: {bot.have_key}")
        print(f"Successfully reached exit: {success}")
    
    return success


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Vault Runner - Mini Programming Language Interpreter")
    parser.add_argument("program", nargs="?", help="Program file path or example name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list-examples", action="store_true", help="List available examples")
    
    args = parser.parse_args()
    
    # Predefined example programs
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
            "description": "Simple corridor navigation - Right-wall-following strategy"
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
            "description": "Corridor navigation with turns"
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
            "description": "Collect keys and open doors, then reach the exit"
        }
    }
    
    if args.list_examples:
        print("Available example programs:")
        for name, example in examples.items():
            print(f"  {name}: {example['description']}")
        return
    
    if not args.program:
        print("Vault Runner - Mini Programming Language Interpreter")
        print("Usage:")
        print("  python main.py <program_file>")
        print("  python main.py <example_name>")
        print("  python main.py --list-examples")
        print("\nExamples:")
        print("  python main.py corridor")
        print("  python main.py examples/collect_and_open.runner")
        return
    
    # Check if it's a predefined example
    if args.program in examples:
        example = examples[args.program]
        print(f"Running example: {args.program}")
        print(f"Description: {example['description']}")
        print(f"Token count: {len(example['source'].split())}")
        print()
        
        success = run_program(
            example['source'],
            example['map'],
            example['start'],
            example['direction'],
            args.verbose
        )
        
        if success:
            print(f"\n✅ Example {args.program} executed successfully!")
        else:
            print(f"\n❌ Example {args.program} execution failed!")
    
    else:
        # Load program from file
        if not os.path.exists(args.program):
            print(f"Error: Program file not found {args.program}")
            print("Available examples: " + ", ".join(examples.keys()))
            return
        
        print(f"Running program file: {args.program}")
        
        # Select appropriate map based on filename
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
            print(f"\n✅ Program {args.program} executed successfully!")
        else:
            print(f"\n❌ Program {args.program} execution failed!")


if __name__ == "__main__":
    main() 