# -*- coding: utf-8 -*-
import re

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


@pytest.mark.parametrize('cmd',
                         ['b'])
def test_invalid_cmd(cmd):
    buffer = Buffer()
    with pytest.raises(NotImplementedError):
        buffer.run(cmd)


@pytest.fixture(scope='function')
def buffer_five():
    return Buffer(['one', 'two', 'three', 'four', 'five'])


def test_empty_cmd_p():
    buffer = Buffer()
    assert buffer.run('p') == []


@pytest.mark.parametrize('cmd, res',
                         [('p', ['five']),
                          ('1p', ['one']),
                          (',2p', ['one', 'two']),
                          ('4,p', ['four', 'five']),
                          ('1,3p', ['one', 'two', 'three']),
                          (',p', ['one', 'two', 'three', 'four', 'five'])])
def test_five_cmd(cmd, res, buffer_five):
    assert buffer_five.run(cmd) == res


@pytest.mark.parametrize('cmd, res', [
    ('1', ((0, 1), None)),
    ('+1', ((None, 1), None)),
    ('-1', ((None, -1), None)),
    ('$', ((0, -1), None)),
    ('1,2', ((0, 1), (0, 2))),
    ('1,', ((0, 1), (0, -1))),
    ('/foo/', ((re.compile(r'foo'), 0), None)),
    ('/foo\/bar/', ((re.compile(r'foo/bar'), 0), None)),
    ('/foo\/bar/-3,/baz/+2', ((re.compile(r'foo/bar'), -3), (re.compile(r'baz'), 2))),
    ])
def test_parse_cmd(cmd, res):
    assert Buffer.parse_cmd(cmd) == res

