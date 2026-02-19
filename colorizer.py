#!/usr/bin/env python3
import re
import os
import select
import shutil
import signal
import sys
import termios
import time
import tty
# Author: Sim Amiral
# Project: PB111 – Code Highlighter
# Read input from stdin and split it into lines
debug_output = sys.stdin.read().splitlines()

interactive = False
if '-i' in sys.argv:
    interactive = True
elif '-r' in sys.argv:
    debug_output= debug_output[-2:]

# Calculate max length
max_length = 0
max_last = 0
for index, line in enumerate(debug_output):
    if "[info]" not in line.lower().split(" "):
        continue
    if '[info]' in line:
        split_line = line.split(" ")  # Split on all whitespace
        if split_line[0] == '[info]':
            count = 1
            if len(split_line[-1]) > max_last:
                max_last = len(split_line[-1])
            while count < len(split_line) and split_line[count] == '':
                count += 1
            if max_length < len(line) + count*3 - len(str(index)):
                max_length = len(line) + count*3 - len(str(index))



tab_amount = 4
bar_width = 7
number_left_pos = 1

info_pattern = r'^\[\d+\]'
hex_pattern = r'^0x[0-9a-fA-F]+$'
hex_pattern_space = r'^0x[0-9a-fA-F]+'
value_pattern = r'^.+\s*(=).+;'
value_pattern = r'^\S.+\s*=\s*.+;' # making it not start with space
return_pattern = r'^return\s+0x[0-9a-fA-F]+'
return_pipe_pattern = r'^return\s+0x[0-9a-fA-F]+\s*│'

value_adder_pattern = r'^(?:\+\+[a-zA-Z0-9_]+;|[a-zA-Z0-9_]+\+\+;)'
function_pattern = r'^.*[\(\[]'
# function_pattern = r'^.*[\(\[].*;$' # improved
# function_pattern = r'^.*\s*=.*;$'
# # function_pattern = r'^[^=]*=[^=]*;$'
# function_pattern = r'^[a-zA-Z0-9_]+\s*=\s*[^=]*;$'
# function_pattern = r'^.*\s*='
function_pattern = r'^([^=]*?)=(\s+)([^;]*);'

assert_pattern = r'^assert\(.*?;\s*'

function_pattern_2 = r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)+\s*│'
function_val = r'^\b[a-zA-Z0-9_]+\s*[)\]]'
last_pattern = r'^(?:&|\);\]|\];|\])|and|;)$'
pattern_val_not = r'^(?:->)?[a-zA-Z]+'
pattern_num_convert = r'^\d+(?=\s|$)'


info_color = '\033[38;5;255m'  # Light blue color for info
reset_color = '' #'{reset_color}'  # Reset color
C_DODGERBLUE1="\033[38;5;39m"
C_SPRINGGREEN2="\033[38;5;47m"
C_GREY70="\033[38;5;249m"
C_GREY50="\033[38;5;244m"
C_SEAGREEN1="\033[38;5;85m"
C_DARKORANGE="\033[38;5;208m"
C_GREY42="\033[38;5;242m"
C_DARKGREEN="\033[38;5;22m"
C_SALMON1="\033[38;5;209m"
C_DARKVIOLET="\033[38;5;92m"
C_PURPLE="\033[38;5;93m"
C_BLUE1="\033[38;5;21m"
CLEAR_LINE  = '\033[2K\r'   # Clear entire line and return carriage
HIGHLITE_BG      = '\033[41m'    # Red background
WHITE_TEXT  = '\033[97m'    # Bright white foreground text
PIPE_COLOR = C_GREY42
C_RED="\033[38;5;9m"

all_colors = [C_RED, PIPE_COLOR, info_color, C_DODGERBLUE1, C_SPRINGGREEN2, C_GREY70, C_SEAGREEN1, C_DARKORANGE, C_GREY42, C_DARKGREEN, C_SALMON1, C_DARKVIOLET, C_PURPLE, C_BLUE1]

output_text = [""]

for index, line in enumerate(debug_output):
    if "warning" in line.lower():
        if interactive:
            output_text.append(f"\033[93m{line}{reset_color}\n")
        else:
            print(f"\033[93m{line}{reset_color}", end='\n')  # Yellow for warnings
        continue
    elif "error" in line.lower():
        if interactive:
            output_text.append(f"\033[91m{line}{reset_color}\n")
        else:
            print(f"\033[91m{line}{reset_color}", end='\n')
        continue
    elif "debug" in line.lower():
        if interactive:
            output_text.append(f"\033[94m{line}{reset_color}\n")  
        else:
            print(f"\033[94m{line}{reset_color}", end='\n')
        continue
    elif ".c" in line.lower():
        if interactive:
            output_text.append(f"\033[92m{line}{reset_color}\n")
        else:
            print(f"\033[92m{line}{reset_color}", end='\n')  # Green for .c files
        continue
    elif "machine failed" in line.lower() or "machine detected" in line.lower():
        if interactive:
            output_text.append(f"{C_RED}{line}\n")
        else:
            print(f"{C_RED}{line}", end='\n')
        continue
    elif "machine halted normally" in line.lower():
        if interactive:
            output_text.append(f"\033[38;5;10m{line}\n")
        else:
            print(f"\033[38;5;10m{line}", end='\n')
        continue
    elif "[info]" not in line.lower():
        if interactive:
            output_text.append(line + '\n')
        else:
            print(line, end='\n')
        continue

    split_line = line.split(" ")  # Split on all whitespace

    output = ''
    if split_line[0] == '[info]':
        output = '[' + str(index) + ']'
    else:
        output = split_line[0]
    
    count = 1
    while count < len(split_line) and split_line[count] == '':
        count += 1
    
    if len(split_line) > 1 and len(split_line[-2]) > 0 and split_line[-2][-1] == ';':
        output += ' '*(count*3-len(str(index))) + " ".join(split_line[count:-1]) 
        output = output.ljust(max_length) + split_line[-1]

        value = int(split_line[-1], 16)
        output = output.ljust(max_length + max_last) + ' │ ' + str(value)
        output = output.ljust(max_length + bar_width + max_last + number_left_pos) + ' │ ' f'0x{value:08X}'

        color_output = ''
        
        while len(output) > 0:
            if re.search(info_pattern, output):
                match = re.search(info_pattern, output)
                for i in match.group(0):
                    if i in ['[', ']'] or i.isdigit():
                        color_output += f'{info_color}{i}{reset_color}'
                    else:
                        color_output += f'{C_BLUE1}{i}{reset_color}'
                # color_output += f'{info_color}{match.group(0)}{reset_color}'
                output = output[match.end():]
            # elif re.search()
            elif re.search(assert_pattern, output):
                # matching assert( cellular_step( 0x0007u ) == 0xfff1u );
                match = re.search(assert_pattern, output)
                sentence = match.group(0)
                output = output[match.end():]

                while sentence:
                    if re.search(r'^assert', sentence):
                        match_ = re.search(r'^assert', sentence)
                        sentence_ = match_.group(0)
                        color_output += f'{C_RED}{sentence_}{reset_color}'
                        sentence = sentence[6:]
                    elif re.search(r'^[a-zA-Z0-9_]+(?=\()', sentence):
                        match_ = re.search(r'^[a-zA-Z0-9_]+(?=\()', sentence)
                        sentence_ = match_.group(0)
                        color_output += f'{C_PURPLE}{sentence_}{reset_color}'
                        sentence = sentence[len(sentence_):]
                    elif re.search(r'^0x[0-9A-Fa-f]+u?', sentence):
                        match_ = re.search(r'^0x[0-9A-Fa-f]+u?', sentence)
                        sentence_ = match_.group(0)
                        color_output += f'{C_BLUE1}{sentence_}{reset_color}'
                        sentence = sentence[len(sentence_):]
                    else:
                        if sentence[0].isdigit() or sentence[0].isalpha():
                            color_output += f'{C_BLUE1}{sentence[0]}{reset_color}'
                        else:
                            color_output += f'{C_GREY42}{sentence[0]}{reset_color}'
                                
                        sentence = sentence[1:]
            elif re.search(function_pattern, output):
                # matching function pattern
                match = re.search(function_pattern, output)
                for i in match.group(0):
                    if i in ['(', ')', '[', ']', '-', '>', '<', '=', '~', '&', '|', '*', '/', '\\', '+', ';']:
                        color_output += f'{C_GREY42}{i}{reset_color}'
                    elif i == '│':
                        color_output += f'{PIPE_COLOR}{i}{reset_color}'
                    else:
                        color_output += f'{C_BLUE1}{i}{reset_color}'
                output = output[match.end():]


            elif re.search(value_adder_pattern, output):
                # matching value adder pattern
                match = re.search(value_adder_pattern, output)
                for i in match.group(0):
                    if i in ['=', ';', '-', '+', '*', '/', '%', '//', '(', ')', '[', ']', '{', '}', ',', ':', '!', '?', '&', '|', '^', '~', '>', '<']:
                        color_output += f'{C_DARKGREEN}{i}{reset_color}'
                    elif i.isdigit():
                        color_output += f'{C_SEAGREEN1}{i}{reset_color}'
                    elif i == '│':
                        color_output += f'{PIPE_COLOR}{i}{reset_color}'
                    else:
                        color_output += f'{C_SPRINGGREEN2}{i}{reset_color}'
                output = output[match.end():]
            # matching value pattern
            elif re.search(value_pattern, output):
                match = re.search(value_pattern, output)
                for i in match.group(0):
                    if i in ['=', ';', '-', '+', '*', '/', '%', '//', '(', ')', '[', ']', '{', '}', ',', ':', '!', '?', '&', '|', '^', '~', '>', '<',';']:
                        color_output += f'{C_GREY42}{i}{reset_color}'
                    elif i.isdigit():
                        color_output += f'{C_SEAGREEN1}{i}{reset_color}'
                    else:
                        color_output += f'{C_SPRINGGREEN2}{i}{reset_color}'
                output = output[match.end():]
            # matching hex pattern on the end
            elif re.search(hex_pattern, output.lower()):
                match = re.search(hex_pattern, output)
                color_output += f'{C_DODGERBLUE1}{match.group(0)}{reset_color}'
                output = output[match.end():]
            # matching return hex pattern on the right side
            elif re.search(hex_pattern_space, output.lower()):
                match = re.search(hex_pattern_space, output)
                color_output += f'{C_DODGERBLUE1}{match.group(0)}{reset_color}'
                output = output[match.end():]
            elif re.search(function_val, output.lower()):
                match = re.search(function_val, output)
                for i in match.group(0):
                    if i in ['=', ';', '-', '+', '*', '/', '%', '//', '(', ')', '[', ']', '{', '}', ',', ':', '!', '?', '&', '|', '^', '~', '>', '<']:
                        color_output += f'{C_GREY42}{i}{reset_color}'
                    elif i == ' ':
                        color_output += ' '
                    else:
                        color_output += f'{C_DARKGREEN}{i}{reset_color}'
                output = output[match.end():]
            elif output[0] in ['=', '<', ';', '&', ']', ')', '}', '*']:
                color_output += f'{C_GREY42}{output[0]}{reset_color}'
                output = output[1:]
            elif re.search(pattern_val_not, output.lower()):
                match = re.search(pattern_val_not, output.lower())

                for i in match.group(0):
                    if i in ['-', '>']:
                        color_output += f'{C_GREY42}{i}{reset_color}'
                    elif i == ' ':
                        color_output += ' '
                    else:
                        color_output += f'{C_DARKGREEN}{i}{reset_color}'
                output = output[match.end():]
            elif re.search(pattern_num_convert, output):
                # match the converted number on right
                match = re.search(pattern_num_convert, output)
                color_output += f'{C_BLUE1}{match.group(0)}{reset_color}'
                output = output[match.end():]
            else:
                if output[0] != '│':
                    color_output += f'{C_GREY42}{output[0]}{reset_color}'
                else:
                    color_output += output[0]
                output = output[1:]
        if interactive:
            output_text.append(color_output + '\n')
        else:
            print(color_output, end='\n')
    else:
        # print(split_line)
        # continue
        # exit()
        output += ' '*(count*3-len(str(index))) + " ".join(split_line[count:])
        output = output.ljust(max_length+max_last) + ' │ '
        output = output.ljust(max_length+ bar_width + max_last + number_left_pos) + ' │ '
        for i in split_line:
            if i[:2] == '0x':
                i = i.strip().rstrip(',')  # clean trailing commas
                dec_value = str(int(i, 16))
                # Right align in 6 characters, pad with spaces on the left
                output += dec_value.ljust(7)

        color_output = ''
        while len(output) > 0:
            if re.search(info_pattern, output):
                match = re.search(info_pattern, output)
                for i in match.group(0):
                    if i in ['[', ']'] or i.isdigit():
                        color_output += f'{info_color}{i}{reset_color}'
                    else:
                        color_output += f'{C_BLUE1}{i}{reset_color}'
                # color_output += f'{info_color}{match.group(0)}{reset_color}'
                output = output[match.end():]
            elif re.search(function_pattern_2, output):
                # matching function pattern
                match = re.search(function_pattern_2, output)
                for i in match.group(0):
                    if i == '(' or i == ')':
                        color_output += f'{C_GREY42}{i}{reset_color}'
                    elif i == '│':
                        color_output += f'{PIPE_COLOR}{i}{reset_color}'
                    else:
                        color_output += f'{C_PURPLE}{i}{reset_color}'
                output = output[match.end():]
            elif re.search(hex_pattern, output.lower()):
                match = re.search(hex_pattern, output)
                color_output += f'{C_DODGERBLUE1}{match.group(0)}{reset_color}'
                output = output[match.end():]
            elif re.search(r'^return\s+0x[0-9a-fA-F]+\s*', output.lower()):
                # matching return output
                match = re.search(r'^return\s+0x[0-9a-fA-F]+\s*│\s*', output)
                color_output += f'{C_SALMON1}{match.group(0)[:6]}{reset_color}'
                color_output += f'{C_GREY42}{match.group(0)[6:-2]}{reset_color}'
                color_output += f'{PIPE_COLOR} {match.group(0)[-1]}{reset_color}'

                output = output[match.end():]
            elif output[0] == '│':
                color_output += f'{PIPE_COLOR}{output[0]}{reset_color}'
                output = output[1:]
            else:
                color_output += output[0]
                output = output[1:]

        if interactive:
            output_text.append(color_output + '\n')
        else:   
            print(color_output, end='\n')


if not interactive:
    print('\033[0m', end='')
    exit(0)
# application part


reset_color = '\033[0m'


"""
Interactive pager for coloured debug output.

Changes vs. the previous version
--------------------------------
* **Minimal redraw when the cursor moves inside the current page.**  Only the
  *previous* cursor line and the *new* cursor line are re‑rendered instead of
  the whole page, eliminating flicker and speeding things up dramatically.
* Full redraw is still performed whenever the visible window (`pos`) changes
  (page‑down, page‑up, scroll past top/bottom, terminal resize, explicit `r`).
* The status bar is only refreshed when it needs to change.

The rest of the behaviour is unchanged.
"""


# ANSI escape sequences for styling and clearing
CLEAR_LINE = "\033[2K"
HIGHLITE_BG = "\033[48;5;240m\033[38;5;230m"  # grey bg, near-white fg
NORMAL_FG = "\033[31m"  # red-ish
RESET = "\033[0m"

def get_terminal_height() -> int:
    """Return usable number of rows (minus 1 for status bar)."""
    return shutil.get_terminal_size((80, 20)).lines - 1

def enable_mouse() -> None:
    print("\033[?1000h\033[?1006h", end='', flush=True)

def disable_mouse() -> None:
    print("\033[?1000l\033[?1006l", end='', flush=True)

def set_raw(fd: int):
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    return old_settings

def restore_term(fd: int, old_settings) -> None:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def read_keys_nonblocking(fd: int):
    keys = []
    while True:
        r, _, _ = select.select([fd], [], [], 0)
        if not r:
            break
        try:
            chunk = os.read(fd, 8).decode(errors="ignore")
            if chunk:
                keys.append(chunk)
            else:
                break
        except BlockingIOError:
            break
    return keys

def place_cursor(row: int, col: int = 1) -> None:
    """Move terminal cursor to absolute position (1-based)."""
    print(f"\033[{row};{col}H", end='')

def draw_status_bar(pos: int, height: int, total: int) -> None:
    place_cursor(height + 1)
    print(f"{CLEAR_LINE}[Lines {pos + 1}-{min(pos + height, total)} of {total}] ↑↓ Scroll", end="", flush=True)

def draw_full_page(lines, pos, height, cursor) -> None:
    """Redraw the whole viewport, fully clearing each line."""
    print("\033[H\033[J", end='')  # Move cursor home + clear screen

    visible = lines[pos:pos + height]

    for i in range(height):
        place_cursor(i + 1)
        if i < len(visible):
            line = visible[i].rstrip('\r\n')
            if i == cursor:
                print(f"{CLEAR_LINE}{HIGHLITE_BG}{line}{RESET}", flush=True)
            else:
                print(f"{CLEAR_LINE}{NORMAL_FG}{line}{RESET}", flush=True)
        else:
            # empty line, just clear it
            print(f"{CLEAR_LINE}", flush=True)

    draw_status_bar(pos, height, len(lines))
    print("\033[J", end="", flush=True)  # clear everything below cursor

def redraw_two_lines(lines, pos, old_cursor, new_cursor) -> None:
    """Unhighlight old line and highlight new line with full line clearing."""
    # Unhighlight old line
    place_cursor(old_cursor + 1)
    old_line = lines[pos + old_cursor].rstrip('\r\n')
    print(f"{CLEAR_LINE}{NORMAL_FG}{old_line}{RESET}", flush=True)

    # Highlight new line
    place_cursor(new_cursor + 1)
    new_line = lines[pos + new_cursor].rstrip('\r\n')
    print(f"{CLEAR_LINE}{HIGHLITE_BG}{new_line}{RESET}", flush=True)

def pager(lines):
    height = get_terminal_height()
    total = len(lines)

    # Start at the end (like less +F)
    pos = max(0, total - height)
    cursor = min(height - 1, total - 1 - pos)

    fd = os.open("/dev/tty", os.O_RDONLY | os.O_NONBLOCK)
    old_settings = set_raw(fd)

    draw_full_page(lines, pos, height, cursor)

    try:
        while True:
            keys = read_keys_nonblocking(fd)
            if not keys:
                time.sleep(0.01)
                continue

            for key in keys:
                if key == "q":
                    return
                elif key in {"R", "r"}:
                    # full refresh
                    print("\033c", end="")  # reset terminal
                    enable_mouse()
                    draw_full_page(lines, pos, height, cursor)
                elif key == " ":
                    # page down
                    if pos + height < total:
                        pos = min(pos + height, total - height)
                        cursor = min(cursor, total - 1 - pos)
                        draw_full_page(lines, pos, height, cursor)
                elif key == '\x1b[B' or key.startswith('\x1b[<65'):  # down arrow / scroll wheel down
                    if cursor < min(height - 1, total - 1 - pos):
                        old_cursor = cursor
                        cursor += 1
                        redraw_two_lines(lines, pos, old_cursor, cursor)
                    elif pos + height < total:
                        pos += 1
                        draw_full_page(lines, pos, height, cursor)
                elif key == '\x1b[A' or key.startswith('\x1b[<64'):  # up arrow / scroll wheel up
                    if cursor > 0:
                        old_cursor = cursor
                        cursor -= 1
                        redraw_two_lines(lines, pos, old_cursor, cursor)
                    elif pos > 0:
                        pos -= 1
                        draw_full_page(lines, pos, height, cursor)

            # Check terminal resize
            new_height = get_terminal_height()
            if new_height != height:
                height = new_height
                cursor = min(cursor, height - 1)
                draw_full_page(lines, pos, height, cursor)

    finally:
        restore_term(fd, old_settings)
        os.close(fd)

def cleanup(*_):
    disable_mouse()
    print(f"{RESET}\n", end="")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    enable_mouse()
    try:
        pager(output_text)
    finally:
        cleanup()

if __name__ == "__main__":
    main()
