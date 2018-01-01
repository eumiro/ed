#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re


class Buffer:
    def __init__(self, lines=None):
        if lines is None:
            self.lines = []
        else:
            self.lines = [str(line) for line in lines]
        self.cur = len(self.lines) - 1
        self.marks = {}
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
            ((?P<b_0>{addr})(?P<b_1>{suff})
             (?P<b>)
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

    def find_addr(self, addr, suff):
        if not addr:
            pos = None
        elif addr == '.':
            pos = self.cur
        elif addr == '$':
            pos = len(self.lines) - 1
        elif addr[0].isdigit():
            pos = int(addr) - 1
        elif addr.startswith(('-', '+')):
            if addr.endswith('-'):
                pos = self.cur - len(addr)
            elif addr.endswith('+'):
                pos = self.cur + len(addr)
            else:
                pos = self.cur + int(addr)
        elif addr.startswith("'"):
            pos = self.marks[addr[1]]
        elif addr.startswith('/'):
            for i in range(len(self.lines)):
                if addr[1:-1] in self.lines[(self.cur + i) % len(self.lines)]:
                    pos = (self.cur + i) % len(self.lines)
                    break
            else:
                raise ValueError()
        elif addr.startswith('?'):
            for i in range(len(self.lines)):
                if addr[1:-1] in self.lines[(self.cur - i) % len(self.lines)]:
                    pos = (self.cur - i) % len(self.lines)
                    break
            else:
                raise ValueError()
        else:
            raise ValueError()

        if suff:
            if suff.endswith('-'):
                pos -= len(suff)
            elif suff.endswith('+'):
                pos += len(suff)
            else:
                pos += int(suff)
        if pos is not None:
            assert 0 <= pos < len(self.lines)
        return pos

    def run(self, cmd):
        act = self.parse_cmd(cmd)
        if act['sect'] == 'c':
            pos0 = self.find_addr(act['addr0'], act['suff0'])
            pos1 = self.find_addr(act['addr1'], act['suff1'])
            if pos1 is None:
                pos1 = len(self.lines) - 1
            if None not in (pos0, pos1):
                assert pos0 <= pos1
            if act['sep']:
                output = slice(pos0, pos1 + 1)
                self.cur = pos1
            elif pos0 is None:
                output = slice(self.cur, self.cur + 1)
            else:
                output = slice(pos0, pos0 + 1)
            if act['action'] == 'p':
                return self.lines[output]
            elif act['action'] == 'l':
                return [line.replace('$', '\\$') + '$' for line in self.lines[output]]
            elif act['action'] == 'n':
                return [f'{i+1}\t{self.lines[i]}'
                        for i in range(*output.indices(len(self.lines)))]


    def parse_cmd(self, cmd):
        match = self.re_cmd.match(cmd)
        if match:
            act = {k: v
                   for k, v in match.groupdict().items()
                   if v is not None}
            sect, verb = min(act.items())
            if sect == 'c':
                return {'sect': 'c',
                        'action': verb,
                        'addr0': act['c_0'],
                        'suff0': act['c_1'],
                        'sep': act['c_2'],
                        'addr1': act['c_3'],
                        'suff1': act['c_4']}
            else:
                return True
        else:
            return False
