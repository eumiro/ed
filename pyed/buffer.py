#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re


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

    @staticmethod
    def match_address(cmd, default):
        if cmd.startswith(tuple('0123456789')):
            match = re.match(r'^(\d+)(.*)$', cmd)
            return (0, int(match.group(1))), match.group(2)
        elif cmd.startswith(('-', '+')):
            match = re.match(r'^([-+]\d+)(.*)$', cmd)
            return (None, int(match.group(1))), match.group(2)
        elif cmd.startswith('$'):
            return (0, -1), cmd[1:]
        else:
            return default, cmd

    @staticmethod
    def parse_cmd(cmd):
        start, rest = Buffer.match_address(cmd, default=(0, 0))
        if rest.startswith(','):
            end, rest = Buffer.match_address(rest[1:], default=(0, -1))
        else:
            end = None
        return (start, end)
