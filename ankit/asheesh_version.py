def cc_total_estimate(community_lic2hits,
                      search_engine_lic2hits):
    '''Input: a dictionary mapping license names to hit counts,
    one from some community like Flickr, and another from a search
    engine like Google.
    Output: A scaled version of the search_engine_lic2hits.'''

    assert community_lic2hits.keys() == search_engine_lic2hits.keys()
    # The dictionaries had better be talking about the same sort of thing
    
    # Prepare a dictionary of the deltas
    diff_dict = {}
    for key in community_lic2hits:
        diff_dict[key] = search_engine_lic2hits[key] - community_lic2hits[key]
    
    # Find the smallest key
    expanded = [ (diff_dict[key], key) for key in diff_dict ]
    min_diff, min_key = min(sorted(expanded))

    # Create a scaling factor of something - what does this mean?
    scaling_factor = (1.0 - (float(min_diff) / search_engine_lic2hits[key]))

    # Scale and return
    ret = {}
    for lic in search_engine_lic2hits:
        ret[lic] = search_engine_lic2hits[lic] * scaling_factor
    return ret
