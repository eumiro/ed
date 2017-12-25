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
