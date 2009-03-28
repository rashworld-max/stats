import linkback_reader
import ccquery

def test_query():
    data = linkback_reader.most_recent()
    q = ccquery.CCQuery()
    q.add_linkbacks(data)
    s = ccquery.Stats(q.license_world())
    print s.freedom_score
    for lic, count in s.licenses.items():
        print lic, ':', count
    print
    s = ccquery.Stats(q.license_by_juris('sg'))
    print s.freedom_score
    for lic, count in s.licenses.items():
        print lic, ':', count
    print

def test_csv():
    data = linkback_reader.most_recent()
    for line in data:
        print line

    
if __name__=='__main__':
    #test_csv()
    test_query()
