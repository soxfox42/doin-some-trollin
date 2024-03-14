#!/usr/bin/env python3

import re
import sys


class IfGotoSyntaxError(Exception):
    pass


class BufferedInput:
    def __init__(self):
        self.buffer = ""
        self.eof = False

    def read(self):
        if not self.buffer and not self.eof:
            try:
                self.buffer = input() + "\n"
            except EOFError:
                self.eof = True
        if self.eof:
            return 0
        first, self.buffer = self.buffer[0], self.buffer[1:]
        return ord(first) & 0xFF


def interpreter(path):
    ram = [0] * 65536
    adr = 0
    pc = 0
    buf_input = BufferedInput()

    # File opening
    with open(path, "r") as file:
        lines = file.readlines()

    # Running
    while pc < len(lines):
        line = lines[pc]

        # Removing comments
        line = re.sub(r"//.*", "", line)

        # Removing spaces and tabs
        line = line.strip()

        # Skip the empty lines
        if not line:
            pc += 1
            continue

        if not line.startswith("if "):
            raise IfGotoSyntaxError(f"Expected 'if' on line {pc}")

        line = line[3:]

        # Splitting the string into a condition and an action
        parts = line.split(":")
        condition = parts[0].strip()
        action = parts[1].strip()

        # Checking the condition
        condition_met = False

        if condition == "1":
            condition_met = True
        elif condition == "0":
            condition_met = False
        elif condition.startswith("ram "):
            num = int(condition[3:])
            condition_met = ram[adr] == num
        elif condition.startswith("adr "):
            num = int(condition[3:])
            condition_met = adr == num
        else:
            raise IfGotoSyntaxError(f"Unknown condition '{condition}' on line {pc}")

        # Perfoming an action
        if condition_met:
            if action == "ram":
                print(chr(ram[adr]), end="")
            elif action == ">ram":
                ram[adr] = buf_input.read()
            elif action == "ram++":
                ram[adr] = (ram[adr] + 1) & 0xFF
            elif action == "ram--":
                ram[adr] = (ram[adr] - 1) & 0xFF
            elif action == "adr++":
                adr = (adr + 1) & 0xFFFF
            elif action == "adr--":
                adr = (adr - 1) & 0xFFFF
            elif action.startswith("goto "):
                goto = int(action[4:])

                if goto <= 0:
                    sys.exit(-goto)

                pc = goto - 1
                continue
            else:
                raise IfGotoSyntaxError(f"Unknown action '{action}' on line {pc}")

        pc += 1


if len(sys.argv) < 2:
    sys.exit("Usage: interpreter.py source.igc")
code_path = sys.argv[1]

interpreter(code_path)
