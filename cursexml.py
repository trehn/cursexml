#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import curses
from sys import argv

from lxml import etree


WHITE = 0
GREEN = 1
BLUE = 2
RED = 3


def pretty_text(text, indent_level=0):
    text = text.strip()
    if "\n" in text:
        indented_text = ""
        for line in text.split("\n"):
            if line.strip():
                indented_text += indent_level * "\t" + line.strip() + "\n"
        text = indented_text.rstrip()
    return text


class XMLProxy(object):
    def __init__(self, filename, stdscr):
        self.etree = etree.parse(filename)
        self.stdscr = stdscr

    def add_element(self, element, lineno, indent_level=0):
        text = pretty_text(element.text.decode('utf-8'), indent_level=indent_level+1)
        if "\n" not in text and len(text) < 5 and not list(element):
            self.add_str(lineno, 0, indent_level * "\t" + "<" + element.tag + ">" + text + "</" + element.tag + ">\n")
            return lineno

        self.add_str(lineno, 0, indent_level * "\t" + "<" + element.tag + ">", BLUE)
        if text:
            for line in text.split("\n"):
                lineno += 1
                self.add_str(lineno, 0, line, color=RED, eol=True)

        for child in element:
            lineno += 1
            lineno = self.add_element(child, lineno, indent_level=indent_level+1)

        lineno += 1
        self.add_str(lineno, 0, indent_level * "\t" + "</" + element.tag + ">", BLUE, eol=True)
        return lineno

    def draw(self, pos_y, pos_x):
        self.content = []
        self.lines_drawn = 0
        self.line_lengths = {}

        self.size_y, self.size_x = self.stdscr.getmaxyx()
        at_bottom = False
        longest_line = 999 #max(self.line_lengths.values())

        self.add_element(self.etree.getroot(), 0)

        return (at_bottom, longest_line)

    def add_str(self, line, column, s, color=WHITE, eol=False):
        if self.line_lengths.get(line, 0) < len(s):
            self.line_lengths[line] = len(s)
        self.stdscr.addstr(line, 0, s[column:].encode('utf-8'), curses.color_pair(color))
        if eol:
            self.stdscr.clrtoeol()


def main(stdscr, filename):
    curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(RED, curses.COLOR_RED, curses.COLOR_BLACK)
    xml = XMLProxy(filename, stdscr)
    pos_y = 0
    pos_x = 0
    at_bottom, longest_line = xml.draw(pos_y, pos_x)
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
        at_bottom, longest_line = xml.draw(pos_y, pos_x)


if __name__ == '__main__':
    try:
        filename = argv[1]
    except IndexError:
        filename = None
    curses.wrapper(main, filename)
