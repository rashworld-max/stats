import sys
sys.path.append('..')

import altgoogle

def test_simple_linkback():
    assert altgoogle.count('link:http://www.google.com/') > 0
