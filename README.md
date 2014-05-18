This is a not-very-serious attempt at a command-line XML viewer that does pretty-printing, syntax highlighting, and someday maybe node folding.

I started this to learn more about curses, so I'm duplicating a lot of stuff you could otherwise accomplish by piping `xmllint` into `less`.

One major caveat is that performance will degrade the further down you scroll in a large file.
