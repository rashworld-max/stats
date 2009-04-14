
# Writes Mike:

#I think we should drop the scaling attempt altogether.  Instead, the
#total minimum estimate sums a number we've arrived at for each and
#every license URI.  We arrive at the minimum number for each license
#URI by taking the larger of the number returned by Yahoo and the
#number summed from known content repositories.  RIght now, this means
#we'd take the Flickr number for the six 2.0 generic licenses and the
#Yahoo number for everything else (this would obtain an estimate of
#230m currently).  As we get good data from other repositories, that
#will change.

def merge_dicts_max_keys(*license2counts):
    '''Take a bunch of dictionaries, and for the keys they share,
    keep only the maximum value for that key.

    >>> merge_dicts_max_keys({'a': 3, 'b': 4}, {'a': 2, 'b': 8})
    {'a': 3, 'b': 8}
    '''

    ret = {}
    all_keys = set()

    # Figure out the keys we'll need
    for license2count in license2counts:
        all_keys.update(license2count.keys())

    # find the max value, and jam it into ret
    for key in all_keys:
        ret[key] = max([d.get(key, 0) for d in license2counts])

    # return that merged dict
    return ret

def total_minimum_estimate(*data_sources):
    '''This function takes a list of dictionaries mapping from
    license URIs to counts as seen. It calculates the maximum seen
    per-license and sums them.

    >>> total_minimum_estimate({'a': 3, 'b': 4}, {'a': 2, 'b': 8})
    11
    '''
    merged = merge_dicts_max_keys(*data_sources)
    return sum(merged.values())

if __name__ == "__main__":
    import doctest
    doctest.testmod()

