import curses


def draw(stdscr, pos_y, pos_x):
    size_y, size_x = stdscr.getmaxyx()
    at_bottom = False
    longest_line = 0
    for lineno in range(size_y):
        line = get_line(pos_y + lineno)
        if line is None:
            at_bottom = True
            stdscr.clrtobot()
            break
        if len(line) > longest_line:
            longest_line = len(line)
        stdscr.addstr(lineno, 0, line[pos_x:pos_x+size_x-1])
        stdscr.clrtoeol()
    stdscr.refresh()
    return (at_bottom, longest_line)


def get_line(line):
    if line > 520:
        return None
    else:
        return "{}: {} F".format(line, 280 * "x")


def main(stdscr):
    pos_y = 0
    pos_x = 0
    size_y, size_x = stdscr.getmaxyx()
    at_bottom, longest_line = draw(stdscr, pos_y, pos_x)
    while True:
        try:
            k = stdscr.getkey()
        except KeyboardInterrupt:
            break
        if k == "q":
            break
        elif k == "KEY_RESIZE":
            pass  # avoid else to just do the redraw
        elif k == "KEY_UP":
            if pos_y > 0:
                pos_y -= 1
        elif k == "KEY_DOWN":
            if not at_bottom:
                pos_y += 1
        elif k == "KEY_LEFT":
            if pos_x > 0:
                pos_x -= 1
        elif k == "KEY_RIGHT":
            if longest_line - pos_x >= size_x:
                pos_x += 1
        else:
            continue
        at_bottom, longest_line = draw(stdscr, pos_y, pos_x)


if __name__ == '__main__':
    curses.wrapper(main)
