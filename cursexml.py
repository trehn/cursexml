#!/usr/bin/env python3
from argparse import ArgumentParser
import curses

from lxml import etree


WHITE = 0
BLUE = 1
CYAN = 2
GREEN = 3
RED = 4
MAGENTA = 5
YELLOW = 6


class EndOfViewPort(Exception):
    pass


def clean_tag(tag):
    if tag.startswith("{"):
        tag = tag.split("}", 1)[1]
    return tag


def strip_text(text):
    text = text.strip()
    if "\n" in text:
        stripped_text = ""
        for line in text.split("\n"):
            if line.strip():
                stripped_text += line.strip() + "\n"
        text = stripped_text.rstrip()
    return text


class XMLProxy(object):
    def __init__(self, filename, stdscr):
        self.etree = etree.parse(filename)
        self.show_indent_guides = True
        self.stdscr = stdscr
        self.pos_x = 0
        self.pos_y = 0

    def add_element(self, element, lineno, indent_level=0):
        # <tag
        self.add_indent(lineno, level=indent_level)
        self.add_str(lineno, "<", color=CYAN)
        self.add_str(lineno, clean_tag(element.tag), color=CYAN, bold=True)

        # <tag attr="value"
        for attr, value in sorted(element.items()):
            self.add_str(lineno, " " + attr, color=YELLOW, bold=True)
            self.add_str(lineno, "=\"", color=YELLOW)
            self.add_str(lineno, value, color=MAGENTA)
            self.add_str(lineno, "\"", color=YELLOW)

        if element.text is None:
            # <tag attr="value" />
            self.add_str(lineno, " />", color=CYAN)
            return lineno
        elif not list(element) and not element.text.strip():
            # <tag></tag>
            self.add_str(lineno, "></", color=CYAN)
            self.add_str(lineno, clean_tag(element.tag), color=CYAN, bold=True)
            self.add_str(lineno, ">", color=CYAN)
            return lineno

        # <tag>
        self.add_str(lineno, ">", color=CYAN)
        text = strip_text(element.text)

        if "\n" not in text and len(text) < 36 and not list(element):
            # <tag>short text</tag>
            self.add_str(lineno, text, color=RED)
            self.add_str(lineno, "</", color=CYAN)
            self.add_str(lineno, clean_tag(element.tag), color=CYAN, bold=True)
            self.add_str(lineno, ">", color=CYAN)
            return lineno

        if text:
            # <tag>
            #     longer or
            #     multiline text
            for line in text.split("\n"):
                lineno += 1
                self.add_indent(lineno, level=indent_level+1)
                self.add_str(lineno, line, color=RED)

        for child in element:
            # <tag>
            #     <child>
            #     </child>
            lineno += 1
            lineno = self.add_element(child, lineno, indent_level=indent_level+1)

        # <tag>
        # </tag>
        lineno += 1
        self.add_indent(lineno, level=indent_level)
        self.add_str(lineno, "</", color=CYAN)
        self.add_str(lineno, clean_tag(element.tag), color=CYAN, bold=True)
        self.add_str(lineno, ">", color=CYAN)
        return lineno

    def draw(self):
        self.line_lengths = {}
        self.size_y, self.size_x = self.stdscr.getmaxyx()

        self.stdscr.erase()
        try:
            self.add_element(self.etree.getroot(), 0)
            at_bottom = True
        except EndOfViewPort:
            at_bottom = False
        longest_line = max(self.line_lengths.values())
        return (at_bottom, longest_line)

    def add_str(self, line, s, color=WHITE, bold=False, indent=0):
        if line >= self.pos_y + self.size_y:
            raise EndOfViewPort
        if line < self.pos_y:
            return
        prev_line_length = self.line_lengths.get(line, 0)
        self.line_lengths[line] = prev_line_length + len(s)
        if bold:
            attrs = curses.color_pair(color) | curses.A_BOLD
        else:
            attrs = curses.color_pair(color)
        self.stdscr.addnstr(
            line - self.pos_y,
            max(prev_line_length - self.pos_x, 0),
            s[max(self.pos_x - prev_line_length, 0):],
            self.size_x - max(prev_line_length - self.pos_x, 0),
            attrs,
        )

    def add_indent(self, lineno, level=0):
        if self.show_indent_guides:
            self.add_str(lineno, "·   " * level, color=BLUE)
        else:
            self.add_str(lineno, "    " * level)


def view_xml(stdscr, filename):
    curses.use_default_colors()
    curses.init_pair(GREEN, curses.COLOR_MAGENTA, -1)
    curses.init_pair(BLUE, curses.COLOR_BLUE, -1)
    curses.init_pair(RED, curses.COLOR_RED, -1)
    curses.init_pair(CYAN, curses.COLOR_CYAN, -1)
    curses.init_pair(MAGENTA, curses.COLOR_MAGENTA, -1)
    curses.init_pair(YELLOW, curses.COLOR_YELLOW, -1)
    xml = XMLProxy(filename, stdscr)
    at_bottom, longest_line = xml.draw()
    while True:
        size_y, size_x = stdscr.getmaxyx()
        try:
            key = stdscr.getkey()
        except KeyboardInterrupt:
            break
        if key in ("g", "KEY_HOME"):
            xml.pos_y = 0
            xml.pos_x = 0
        elif key == "i":
            xml.show_indent_guides = not xml.show_indent_guides
        elif key == "q":
            break
        elif key == "KEY_RESIZE":
            pass  # avoid else to just do the redraw
        elif key == "KEY_UP" or key == "k":
            if xml.pos_y > 0:
                xml.pos_y -= 1
        elif key == "KEY_DOWN" or key == "j":
            if not at_bottom:
                xml.pos_y += 1
        elif key == "KEY_LEFT" or key == "h":
            if xml.pos_x > 0:
                xml.pos_x -= 1
        elif key == "KEY_RIGHT" or key == "l":
            if longest_line - xml.pos_x >= size_x:
                xml.pos_x += 1
        elif key == "KEY_NPAGE" or key == "\x06":  # ^F
            if not at_bottom:
                xml.pos_y += size_y
        elif key == "KEY_PPAGE" or key == "\x02":  # ^B
            if xml.pos_y > 0:
                xml.pos_y = max(0, xml.pos_y - size_y)
        else:
            continue
        at_bottom, longest_line = xml.draw()


def main(*args, **kwargs):
    parser = ArgumentParser(prog="cursexml", description="CurseXML - command line XML viewer")
    parser.add_argument(
        'file',
        metavar="FILE",
        type=str,
        help="file to open",
    )
    args = parser.parse_args()
    curses.wrapper(view_xml, args.file)


if __name__ == '__main__':
    main()
