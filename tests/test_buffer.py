# -*- coding: utf-8 -*-
import pytest

from pyed.buffer import Buffer


def test_init_empty_ok():
    assert Buffer()


def test_init_invalid():
    with pytest.raises(TypeError):
        Buffer(x=1)


@pytest.mark.parametrize('lines',
                         [[],
                          [''],
                          ['', ''],
                          ['a'],
                          ['a', 'b'],
                          [1, 'b']])
def test_init_ok(lines):
    assert Buffer(lines)
