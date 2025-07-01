import sys
import re
# Author: Filip Lazor
# Project: PB111 – Code Highlighter
# Read input from stdin and split it into lines
debug_output = sys.stdin.read().splitlines()

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
            while split_line[count] == '':
                count += 1
            if max_length < len(line) + count*3 - len(str(index)):
                max_length = len(line) + count*3 - len(str(index))

interactive = False
if '-i' in sys.argv:
    interactive = True

tab_amount = 4
bar_width = 7
number_left_pos = 1

info_pattern = r'^\[\d+\]'
hex_pattern = r'^0x[0-9a-fA-F]+$'
hex_pattern_space = r'^0x[0-9a-fA-F]+'
value_pattern = r'^.+\s*(=).+;'
return_pattern = r'^return\s+0x[0-9a-fA-F]+'
return_pipe_pattern = r'^return\s+0x[0-9a-fA-F]+\s*│'

value_adder_pattern = r'^(?:\+\+[a-zA-Z0-9_]+;|[a-zA-Z0-9_]+\+\+;)'
function_pattern = r'^.*[\(\[]'
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

all_colors = [PIPE_COLOR, info_color, C_DODGERBLUE1, C_SPRINGGREEN2, C_GREY70, C_SEAGREEN1, C_DARKORANGE, C_GREY42, C_DARKGREEN, C_SALMON1, C_DARKVIOLET, C_PURPLE, C_BLUE1]

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
    while split_line[count] == '':
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
            elif re.search(function_pattern, output):
                # matching function pattern
                match = re.search(function_pattern, output)
                for i in match.group(0):
                    if i in ['(', ')', '[', ']', '-', '>', '<', '=']:
                        color_output += f'{C_GREY42}{i}{reset_color}'
                    elif i == '│':
                        color_output += f'{PIPE_COLOR}{i}{reset_color}'
                    else:
                        color_output += f'{C_PURPLE}{i}{reset_color}'
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
                    if i in ['=', ';', '-', '+', '*', '/', '%', '//', '(', ')', '[', ']', '{', '}', ',', ':', '!', '?', '&', '|', '^', '~', '>', '<']:
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
        output += ' '*(count*3-len(str(index))) + " ".join(split_line[count:])
        output = output.ljust(max_length+max_last) + ' │ '
        output = output.ljust(max_length+ bar_width + max_last + number_left_pos) + ' │ '

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


#!/usr/bin/env python3
import sys, shutil, termios, tty, os, signal, select, time

def get_terminal_height():
    return shutil.get_terminal_size((80, 20)).lines - 1

def enable_mouse():
    print("\033[?1000h\033[?1006h", end='', flush=True)

def disable_mouse():
    print("\033[?1000l\033[?1006l", end='', flush=True)

def set_raw(fd):
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    return old_settings

def restore_term(fd, old_settings):
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def read_keys_nonblocking(fd):
    keys = []
    while True:
        r, _, _ = select.select([fd], [], [], 0)
        if not r:
            break
        try:
            chunk = os.read(fd, 6).decode(errors='ignore')
            if chunk:
                keys.append(chunk)
            else:
                break
        except BlockingIOError:
            break
    return keys


def draw_page(lines, pos, height, cursor):
    print("\033[H", end='')  # Move cursor to top-left
    visible = lines[pos:pos + height]

    for i in range(height):
        if i < len(visible):
            line = visible[i].rstrip('\r\n')  # strip trailing newlines just in case
            if i == cursor:
                print(f"{CLEAR_LINE}{HIGHLITE_BG}{line}{reset_color}", flush=True)
            else:
                print(f"{CLEAR_LINE}\033[31m{line}{reset_color}", flush=True)
        else:
            # Clear empty line completely
            print(f"{CLEAR_LINE}", flush=True)

    # Status bar: clear line fully then print
    print(f"{CLEAR_LINE}[Lines {pos + 1}-{min(pos + height, len(lines))} of {len(lines)}] ↑↓ Scroll", flush=True)
    # Clear everything below the cursor (if terminal is taller than height+1)
    print("\033[J", end='', flush=True)


def pager(lines):
    height = get_terminal_height()
    total = len(lines)
    pos = max(0, total - height)
    cursor = min(height - 1, total - 1 - pos)

    fd = os.open('/dev/tty', os.O_RDONLY | os.O_NONBLOCK)
    old_settings = set_raw(fd)

    draw_page(lines, pos, height, cursor)
    last_draw = time.time()



    try:
        while True:
            keys = read_keys_nonblocking(fd)
            if not keys:
                time.sleep(0.01)
                continue

            for key in keys:
                if key == 'q':
                    return
                elif key == 'R' or key == 'r':
                    print("\033c", end='')  # terminal reset
                    enable_mouse()          # re-enable mouse tracking after reset
                    draw_page(lines, pos, height)
                elif key == ' ':
                    if pos + height < total:
                        pos = min(pos + height, total - height)
                        cursor = min(cursor, total - 1 - pos)
                elif key == '\x1b[B' or key.startswith('\x1b[<65'):
                    if cursor < min(height - 1, total - 1 - pos):
                        cursor += 1
                    else:
                        if pos + height < total:
                            pos += 1
                elif key == '\x1b[A' or key.startswith('\x1b[<64'):
                    if cursor > 1:
                        cursor -= 1
                    else:
                        if pos > 0:
                            pos -= 1
                            cursor = 1

            now = time.time()
            if now - last_draw > 0.02:
                draw_page(lines, pos, height, cursor)
                last_draw = now
    finally:
        restore_term(fd, old_settings)
        os.close(fd)

def cleanup(*_):
    disable_mouse()
    print("{reset_color}\n", end='')
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
