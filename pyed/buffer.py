#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Buffer:
    def __init__(self, lines=None):
        if lines is None:
            self.lines = []
        else:
            self.lines = [str(line) for line in lines]
        self.cur = len(self.lines)

    def __len__(self):
        return len(('\n'.join(self.lines)).encode('utf8'))

    def find_pos(self, raw_pos):
        raw_lower, comma, raw_upper = raw_pos.partition(',')

        if comma:
            if raw_lower.isdigit():
                lower = int(raw_lower)
            elif raw_lower == '':
                lower = 1
            else:
                raise NotImplementedError(f'invalid lower pos {raw_lower!r}')

            if raw_upper.isdigit():
                upper = int(raw_upper)
                self.cur = upper
            elif raw_upper == '':
                upper = len(self.lines)
            else:
                raise NotImplementedError(f'invalid upper pos {raw_upper!r}')
        else:
            if raw_lower.isdigit():
                lower = int(raw_lower)
                upper = lower
            elif raw_lower == '':
                lower = self.cur
                upper = self.cur + 1
            else:
                raise NotImplementedError(f'invalid lower pos {raw_lower!r}')

        return slice(lower - 1, upper)

    def run(self, cmd):
        if cmd.endswith('p'):
            rng = self.find_pos(cmd[:-1])
            if self.cur:
                return self.lines[rng]
            else:
                return []
        else:
            raise NotImplementedError(f'invalid command {cmd}')
