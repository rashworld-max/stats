from sets import Set as set
def list2dict(l):
    ''' Input: a list of even length
    Output: A dict where the odd-numbered elements map to their successors. '''
    assert((len(l) % 2) == 0)
    ret = {}
    i = 0
    while i < len(l):
        ret[l[i]] = l[i+1]
        i += 2
    return ret

def allthesame(l):
    ''' Could do it recursively, but does Python do tail-call optimization? '''
    shrunk = set(l)
    return (len(shrunk) <= 1)

def somedifferent(l):
    shrunk = set(l)
    return (len(shrunk) >= 2)

