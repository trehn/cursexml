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


class EndOfViewPort(Exception):
    pass


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
        self.pos_x = 0
        self.pos_y = 0

    def add_element(self, element, lineno, indent_level=0):
        text = pretty_text(element.text.decode('utf-8'), indent_level=indent_level+1)
        if "\n" not in text and len(text) < 5 and not list(element):
            self.add_str(lineno, indent_level * "\t" + "<" + element.tag + ">" + text + "</" + element.tag + ">\n")
            return lineno

        self.add_str(lineno, indent_level * "\t" + "<" + element.tag + ">", BLUE)
        if text:
            for line in text.split("\n"):
                lineno += 1
                self.add_str(lineno, line, color=RED)

        for child in element:
            lineno += 1
            lineno = self.add_element(child, lineno, indent_level=indent_level+1)

        lineno += 1
        self.add_str(lineno, indent_level * "\t" + "</" + element.tag + ">", BLUE)
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
        #        stdscr.refresh()
        return (at_bottom, longest_line)

    def add_str(self, line, s, color=WHITE):
        if line >= self.pos_y + self.size_y:
            raise EndOfViewPort
        if line < self.pos_y:
            return
        if self.line_lengths.get(line, 0) < len(s):
            self.line_lengths[line] = len(s)
        self.stdscr.addstr(
            line - self.pos_y,
            0,
            s[self.pos_x:].encode('utf-8'),
            curses.color_pair(color),
        )


def main(stdscr, filename):
    curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(RED, curses.COLOR_RED, curses.COLOR_BLACK)
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
        elif key == "q":
            break
        elif key == "KEY_RESIZE":
            pass  # avoid else to just do the redraw
        elif key == "KEY_UP":
            if xml.pos_y > 0:
                xml.pos_y -= 1
        elif key == "KEY_DOWN":
            if not at_bottom:
                xml.pos_y += 1
        elif key == "KEY_LEFT":
            if xml.pos_x > 0:
                xml.pos_x -= 1
        elif key == "KEY_RIGHT":
            if longest_line - xml.pos_x >= size_x:
                xml.pos_x += 1
        elif key == "KEY_NPAGE":
            if not at_bottom:
                xml.pos_y += size_y
        elif key == "KEY_PPAGE":
            if xml.pos_y > 0:
                xml.pos_y = max(0, xml.pos_y - size_y)
        else:
            continue
        at_bottom, longest_line = xml.draw()


if __name__ == '__main__':
    try:
        filename = argv[1]
    except IndexError:
        filename = None
    curses.wrapper(main, filename)
