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
        self.re_cmd = self._init_re_cmd()

    def _init_re_cmd(self):
        addr = r"""
                \.|
                \$|
                [-+]?\d+|
                \++|
                \-+|
                /((\\\/|[^/])*)/|
                \?((\\\?|[^?])*)\?|
                '[a-z]|
                """
        suff = r'[-+]*\d*'
        sep = r',|;|'
        re_cmd = re.compile(rf"""^
            ((?P<_0>{addr})(?P<_1>{suff})
             |
             (?P<a_0>{addr})(?P<a_1>{suff})
             (?P<a>a|i|k[a-z]|s[gpr]*|x|=)
             |
             (?P<c_0>{addr})(?P<c_1>{suff})
             (?P<c_2>{sep})
             (?P<c_3>{addr})(?P<c_4>{suff})
             (?P<c>c|d|j|l|n|p|y)
             |
             (?P<e>[eEf])\s+(?P<e_0>[\w\.]+)
             |
             (?P<h>h|H|P|q|Q|u)
             |
             (?P<m_0>{addr})(?P<m_1>{suff})
             (?P<m_2>{sep})
             (?P<m_3>{addr})(?P<m_4>{suff})
             (?P<m>m|t)
             (?P<m_5>{addr})(?P<m_6>{suff})
             |
             (?P<r_0>{addr})(?P<r_1>{suff})
             (?P<r>r|w|wq|W)\s+(?P<r_2>!?[\w\.]+)
             |
             (?P<s_0>{addr})(?P<s_1>{suff})
             (?P<s_2>{sep})
             (?P<s_3>{addr})(?P<s_4>{suff})
             (?P<s>s)
             /(?P<s_5>(\\\/|[^/])*)/(?P<s_6>(\\\/|[^/])*)/
             (?P<s_7>[g\dlnp]*)
            )$""", re.X)
        return re_cmd

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
        first, second = None, None
        if cmd.startswith('/'):
            match = re.match(r'^/((\\\/|[^/])*)/(.*)$', cmd)
            first = re.compile(match.group(1).replace('\/', '/'))
            second = 0
            cmd = match.group(3)
            if cmd.startswith(tuple('-+0123456789')):
                if len(cmd) > 1 and cmd[1].isdigit():
                    match = re.match(r'^([-+]\d+)(.*)$', cmd)
                    second = int(match.group(1))
                    cmd = match.group(2)
                else:
                    match = re.match(r'^([-+]+)(.*)$', cmd)
                    second = len(match.group(1))
                    if cmd.startswith('-'):
                        second = -second
                    cmd = match.group(2)
        elif cmd.startswith(tuple('0123456789')):
            match = re.match(r'^(\d+)(.*)$', cmd)
            first, second = 0, int(match.group(1))
            cmd = match.group(2)
        elif cmd.startswith(('-', '+')):
            match = re.match(r'^([-+]\d+)(.*)$', cmd)
            first, second = None, int(match.group(1))
            cmd = match.group(2)
        elif cmd.startswith('$'):
            first, second = 0, -1
            cmd = cmd[1:]
        else:
            first, second = default
        return (first, second), cmd

    def parse_cmd(self, cmd):
        match = self.re_cmd.match(cmd)
        return bool(match)
