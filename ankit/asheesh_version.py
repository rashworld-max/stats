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

def usage():
    print """
Howdy!  Here's an example of how to use this program:

$ python asheesh_version.py community=flickr by=3000 by-nc=40000 search_engine=google by=30000 by-nc=400000

And here's what you might get for output:

# Input data:
# community flickr said {'by': 3000, 'by-nc': 40000}
# search engine google said {'by': 30000, 'by-nc': 400000}
A very conservative estimate, based on a method from Singopore by Prof. FIXME with code help from Ankit, of the total spread of CC licenses in the world follows:
by-nc=40333
by=302
"""
def main():
    import sys
    useful_args = sys.argv[1:]
    if not useful_args:
        usage()
        sys.exit(1)
    
    search_engine_data = {}
    community_data = {}
    community_name = None
    search_engine_name = None
    current = None
    for arg in useful_args:
        key, value = arg.split('=')
        if key == 'community':
            community_name = value
            current = community_data
        elif key == 'search_engine':
            search_engine_name = value
            current = search_engine_data
        else:
            assert key not in current
            current[key] = int(value)

    inform_user_of_input(search_engine_data=search_engine_data,
                         community_data=community_data,
                         search_engine_name=search_engine_name,
                         community_name=community_name)

    total_estimate = cc_total_estimate(community_lic2hits=community_data,
                                       search_engine_lic2hits=search_engine_data)
    
    inform_user_of_output(total_estimate)

def inform_user_of_input(search_engine_data, community_data, search_engine_name, community_name):
    print '# Input data'
    print '# community %s said %s' % (community_name, community_data)
    print '# search engine %s said %s' % (search_engine_name, search_engine_data)

def inform_user_of_output(total_estimate):
    print 'A very conservative estimate, based on a method from Singopore by Prof. FIXME with code help from Ankit, of the total spread of CC licenses in the world follows:'
    for key in total_estimate:
        print '%s=%d' % (key, total_estimate[key])
    


if __name__ == '__main__':
    main()

        
