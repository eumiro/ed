# -*- coding: utf-8 -*-
import pytest

from pyed.buffer import Buffer


def test_init_invalid():
    with pytest.raises(TypeError):
        Buffer(x=1)


@pytest.mark.parametrize('lines, size',
                         [(None, 0),
                          ([], 0),
                          ([''], 0),
                          (['', ''], 1),
                          (['a'], 1),
                          (['a', 'b'], 3),
                          ([1, 'b'], 3)])
def test_init_ok_len(lines, size):
    assert len(Buffer(lines)) == size


@pytest.fixture(scope='function')
def buffer_two():
    return Buffer(['one', 'two'])


@pytest.fixture(scope='function')
def buffer_five():
    return Buffer(['one', 'two', 'three', 'four', 'five'])


@pytest.mark.parametrize('cmd, res',
                         [('p', ['five']),
                          ('1p', ['one']),
                          (',2p', ['one', 'two']),
                          ('4,p', ['four', 'five']),
                          ('4,$p', ['four', 'five']),
                          ('1,3p', ['one', 'two', 'three']),
                          (',p', ['one', 'two', 'three', 'four', 'five']),
                          ('n', ['5\tfive']),
                          ('1n', ['1\tone']),
                          (',2n', ['1\tone', '2\ttwo']),
                          ('4,n', ['4\tfour', '5\tfive']),
                          ('4,$n', ['4\tfour', '5\tfive']),
                          ('1,3n', ['1\tone', '2\ttwo', '3\tthree']),
                          (',n', ['1\tone', '2\ttwo', '3\tthree',
                                  '4\tfour', '5\tfive'])])
def test_five_cmd(cmd, res, buffer_five):
    assert buffer_five.run(cmd) == res


@pytest.fixture(scope='function')
def buffer_special():
    return Buffer(['first $ line', '', '\\ third $'])


@pytest.mark.parametrize('cmd, res',
                         [('l', ['\\ third \\$$']),
                          ('1l', ['first \\$ line$']),
                          (',2l', ['first \\$ line$', '$']),
                          ('2,l', ['$', '\\ third \\$$']),
                          ('2,$l', ['$', '\\ third \\$$']),
                          ('1,3l', ['first \\$ line$', '$', '\\ third \\$$']),
                          (',l', ['first \\$ line$', '$', '\\ third \\$$'])])
def test_special_(cmd, res, buffer_special):
    assert buffer_special.run(cmd) == res


@pytest.mark.parametrize('cmd', [r'1',
                                 r'+1',
                                 r'-1',
                                 r'$',
                                 r'$-1',
                                 r'/foo/',
                                 r'/foo\/bar/',
                                 r'/foo\/bar/-3,/baz/+2d',
                                 r'/foo/+',
                                 r'/foo/+1',
                                 r'/foo/++',
                                 r'/foo/---',
                                 r'3a',
                                 r'e test',
                                 r'E test.txt',
                                 r'f test.txt',
                                 r'h',
                                 r'H',
                                 r'P',
                                 r'q',
                                 r'Q',
                                 r'u',
                                 r'/a/,/b/s/c/d/n',
                                 r'w file.txt',
                                 r'W file.txt',
                                 r'r file.txt',
                                 r'r !date',
                                ])
def test_parse_cmd(cmd):
    assert Buffer().parse_cmd(cmd)


@pytest.mark.parametrize('cmd', [(',g/re/p'),
                                 (',G/re/'),
                                 (',v/re/p'),
                                 (',V/re/'),
                                 (',z1'),
                                 ('!ls'),
                                 ('1,2#comment'),
                                ])
def test_parse_cmd_fails(cmd):
    assert not Buffer().parse_cmd(cmd)


def test_set_mark(buffer_five):
    buffer_five.run('2ka')
    buffer_five.run('kb')
    assert buffer_five.run('\'ap') == ['two']
    assert buffer_five.run('\'bp') == ['five']
    assert buffer_five.run('\'a+,\'b-1p') == ['three', 'four']


@pytest.mark.parametrize('cmd, lines, res',
                         [('a', ['x'], ['one', 'two', 'x']),
                          ('1a', ['x'], ['one', 'x', 'two']),
                          ('/tw/a', ['x'], ['one', 'two', 'x']),
                          ('$a', ['x', 'y'], ['one', 'two', 'x', 'y']),
                          ('i', ['x'], ['one', 'x', 'two']),
                          ('1i', ['x'], ['x', 'one', 'two']),
                          ('/tw/i', ['x'], ['one', 'x', 'two']),
                          ('$i', ['x', 'y'], ['one', 'x', 'y', 'two']),
                          ('d', [], ['one']),
                          ('1d', [], ['two']),
                          ('/tw/d', [], ['one']),
                          ('/on/,/tw/d', [], []),
                          (',d', [], []),
                          ])
def test_append(cmd, lines, res, buffer_two):
    buffer_two.run(cmd, lines)
    assert buffer_two.run(',p') == res

