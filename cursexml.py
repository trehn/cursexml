#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import curses
from sys import argv

from lxml import etree


class XMLProxy(object):
    def __init__(self, filename):
        self.etree = etree.parse(filename)

    def add_element(self, element, indent_level=0):
        self.content.append(indent_level * "\t" + "<" + element.tag + ">")
        for child in element:
            self.add_element(child, indent_level=indent_level+1)
        self.content.append(indent_level * "\t" + "</" + element.tag + ">\n")

    def draw(self, stdscr, pos_y, pos_x):
        self.content = []
        self.add_element(self.etree.getroot())

        size_y, size_x = stdscr.getmaxyx()
        at_bottom = False
        longest_line = 0
        for lineno in range(size_y):
            line = self.get_line(pos_y + lineno)
            if line is None:
                at_bottom = True
                stdscr.clrtobot()
                break
            if len(line) > longest_line:
                longest_line = len(line)
            line = line[pos_x:pos_x+size_x-1]
            stdscr.addstr(lineno, 0, line.encode('utf-8'))
            stdscr.clrtoeol()
        stdscr.refresh()
        return (at_bottom, longest_line)

    def get_line(self, lineno):
        try:
            line = self.content[lineno].rstrip()
        except IndexError:
            return None
        return line


def main(stdscr, filename):
    xml = XMLProxy(filename)
    pos_y = 0
    pos_x = 0
    at_bottom, longest_line = xml.draw(stdscr, pos_y, pos_x)
    while True:
        size_y, size_x = stdscr.getmaxyx()
        try:
            key = stdscr.getkey()
        except KeyboardInterrupt:
            break
        if key in ("g", "KEY_HOME"):
            pos_y = 0
            pos_x = 0
        elif key == "q":
            break
        elif key == "KEY_RESIZE":
            pass  # avoid else to just do the redraw
        elif key == "KEY_UP":
            if pos_y > 0:
                pos_y -= 1
        elif key == "KEY_DOWN":
            if not at_bottom:
                pos_y += 1
        elif key == "KEY_LEFT":
            if pos_x > 0:
                pos_x -= 1
        elif key == "KEY_RIGHT":
            if longest_line - pos_x >= size_x:
                pos_x += 1
        elif key == "KEY_NPAGE":
            if not at_bottom:
                pos_y += size_y
        elif key == "KEY_PPAGE":
            if pos_y > 0:
                pos_y = max(0, pos_y - size_y)
        else:
            continue
        at_bottom, longest_line = xml.draw(stdscr, pos_y, pos_x)


if __name__ == '__main__':
    try:
        filename = argv[1]
    except IndexError:
        filename = None
    curses.wrapper(main, filename)
