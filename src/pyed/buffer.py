#!/usr/bin/env python3


import re


class Buffer:
    def __init__(self, lines=None):
        if lines is None:
            self.lines = []
        else:
            self.lines = [str(line) for line in lines]
        self.cur = len(self.lines) - 1
        self.marks = {}
        self.cut_buffer = []
        self.re_cmd = Buffer._init_re_cmd()

    @staticmethod
    def _init_re_cmd():
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
        suff = r"[-+]*\d*"
        sep = r",|;|"
        re_cmd = re.compile(
            rf"""^
            ((?P<b_0>{addr})(?P<b_1>{suff})
             (?P<b>)
             |
             (?P<a_0>{addr})(?P<a_1>{suff})
             (?P<a>a|i|k[a-z]|s[gpr]*|x|=)
             |
             (?P<c_0>{addr})(?P<c_1>{suff})
             (?P<c_2>{sep})
             (?P<c_3>{addr})(?P<c_4>{suff})
             (?P<c>[cdjlnpy])
             |
             (?P<e>[eEf])\s+(?P<e_0>[\w.]+)
             |
             (?P<h>[hHPqQu])
             |
             (?P<m_0>{addr})(?P<m_1>{suff})
             (?P<m_2>{sep})
             (?P<m_3>{addr})(?P<m_4>{suff})
             (?P<m>[mt])
             (?P<m_5>{addr})(?P<m_6>{suff})
             |
             (?P<r_0>{addr})(?P<r_1>{suff})
             (?P<r>r|w|wq|W)\s+(?P<r_2>!?[\w.]+)
             |
             (?P<s_0>{addr})(?P<s_1>{suff})
             (?P<s_2>{sep})
             (?P<s_3>{addr})(?P<s_4>{suff})
             (?P<s>s)
             /(?P<s_5>(\\/|[^/])*)/(?P<s_6>(\\/|[^/])*)/
             (?P<s_7>[g\dlnp]*)
            )$""",
            re.X,
        )
        return re_cmd

    def __len__(self):
        return len(("\n".join(self.lines)).encode("utf8"))

    def find_addr(self, addr, suff):
        if not addr:
            pos = None
        elif addr == ".":
            pos = self.cur
        elif addr == "$":
            pos = len(self.lines) - 1
        elif addr == "0":
            pos = 0
        elif addr[0].isdigit():
            pos = int(addr) - 1
        elif addr.startswith(("-", "+")):
            if addr.endswith("-"):
                pos = self.cur - len(addr)
            elif addr.endswith("+"):
                pos = self.cur + len(addr)
            else:
                pos = self.cur + int(addr)
        elif addr.startswith("'"):
            pos = self.marks[addr[1]]
        elif addr.startswith("/"):
            for i in range(len(self.lines)):
                if addr[1:-1] in self.lines[(self.cur + i) % len(self.lines)]:
                    pos = (self.cur + i) % len(self.lines)
                    break
            else:
                raise ValueError()
        elif addr.startswith("?"):
            for i in range(len(self.lines)):
                if addr[1:-1] in self.lines[(self.cur - i) % len(self.lines)]:
                    pos = (self.cur - i) % len(self.lines)
                    break
            else:
                raise ValueError()
        else:
            raise ValueError()

        if suff:
            if suff.endswith("-"):
                pos -= len(suff)
            elif suff.endswith("+"):
                pos += len(suff)
            else:
                pos += int(suff)

        if pos is not None:
            if not 0 <= pos < len(self.lines):
                raise ValueError()
        return pos

    def run(self, cmd, lines=None):
        if lines is None:
            lines = []
        elif not isinstance(lines, list):
            raise ValueError()
        if lines and lines[-1] == ".":
            lines.pop(-1)

        act = self.parse_cmd(cmd)
        res = []
        if act["sect"] == "a":
            pos0 = self.find_addr(act["addr0"], act["suff0"])
            if pos0 is None:
                pos0 = self.cur
            if act["action"].startswith("k"):
                self.marks[act["action"][1]] = pos0
            elif act["action"] == "a":
                self.lines[pos0 + 1 : pos0 + 1] = lines
            elif act["action"] == "i":
                self.lines[pos0:pos0] = lines
            elif act["action"] == "x":
                self.lines[pos0 + 1 : pos0 + 1] = self.cut_buffer
            elif act["action"] == "=":
                res = str(pos0)

        elif act["sect"] == "c":
            pos0 = self.find_addr(act["addr0"], act["suff0"])
            pos1 = self.find_addr(act["addr1"], act["suff1"])
            if pos1 is None:
                pos1 = len(self.lines) - 1
            if None not in (pos0, pos1):
                if pos1 < pos0:
                    raise ValueError()
            if act["sep"]:
                output = slice(pos0, pos1 + 1)
                self.cur = pos1
            elif pos0 is None:
                output = slice(self.cur, self.cur + 1)
            else:
                output = slice(pos0, pos0 + 1)
            if act["action"] == "p":
                res = self.lines[output]
                self.cur = output.stop
            elif act["action"] == "l":
                res = [
                    line.replace("$", "\\$") + "$"
                    for line in self.lines[output]
                ]
                self.cur = output.stop
            elif act["action"] == "n":
                res = [
                    f"{i+1}\t{self.lines[i]}"
                    for i in range(*output.indices(len(self.lines)))
                ]
                self.cur = output.stop
            elif act["action"] == "y":
                self.cut_buffer = self.lines[output]
            elif act["action"] == "d":
                self.cut_buffer = self.lines[output]
                self.lines[output] = []
            elif act["action"] == "j":
                self.cut_buffer = self.lines[output]
                self.lines[output] = ["".join(self.lines[output])]
            elif act["action"] == "c":
                self.lines[output] = lines
        elif act["sect"] == "m":
            pos0 = self.find_addr(act["addr0"], act["suff0"])
            pos1 = self.find_addr(act["addr1"], act["suff1"])
            pos2 = self.find_addr(act["addr2"], act["suff2"])
            if pos1 is None:
                pos1 = len(self.lines) - 1
            if None not in (pos0, pos1):
                if pos1 < pos0:
                    raise ValueError()
            if act["sep"]:
                output = slice(pos0, pos1 + 1)
                self.cur = pos1
            elif pos0 is None:
                output = slice(self.cur, self.cur + 1)
            else:
                output = slice(pos0, pos0 + 1)
            if act["action"] == "m":
                if pos2 < output.start:
                    tmp = self.lines[output]
                    self.lines[output] = []
                    self.lines[pos2 + 1 : pos2 + 1] = tmp
                elif pos2 == output.start:
                    pass
                elif pos2 >= output.stop:
                    self.lines[pos2 + 1 : pos2 + 1] = self.lines[output]
                    self.lines[output] = []
                else:
                    raise ValueError()
            elif act["action"] == "t":
                self.lines[pos2 + 1 : pos2 + 1] = self.lines[output]
        return res

    def parse_cmd(self, cmd):
        match = self.re_cmd.match(cmd)
        if match:
            act = {k: v for k, v in match.groupdict().items() if v is not None}
            sect, verb = min(act.items())
            if sect == "a":
                res = {
                    "sect": "a",
                    "action": verb,
                    "addr0": act["a_0"],
                    "suff0": act["a_1"],
                }
            elif sect == "c":
                res = {
                    "sect": "c",
                    "action": verb,
                    "addr0": act["c_0"],
                    "suff0": act["c_1"],
                    "sep": act["c_2"],
                    "addr1": act["c_3"],
                    "suff1": act["c_4"],
                }
            elif sect == "m":
                res = {
                    "sect": "m",
                    "action": verb,
                    "addr0": act["m_0"],
                    "suff0": act["m_1"],
                    "sep": act["m_2"],
                    "addr1": act["m_3"],
                    "suff1": act["m_4"],
                    "addr2": act["m_5"],
                    "suff2": act["m_6"],
                }
            else:
                res = True
        else:
            res = False
        return res
