# -*- coding: utf-8 -*-
import sys
import re
import gzip

data_from_logs = []

groupedJuris = []
groupedJurisCode = []
groupedCount = []

### Consider Me: A CSV parser instead of crummy regex
### ADD ME: Additional code to identify which file to use as input when asked to grab the latest file, given the stats dir

"""     dirlist = [d for d in os.listdir(dir) if os.path.isdir(d)] #Uses the OS module to get a directory listing for the argument dir (folders only)
     dirlist.sort() #Sorts the directory listing
     latest = dirlist[len(dirlist)] #Grabs the latest folder."""

### Still need to navigate to the timestamp folder within and get hold of the relevant CSV. Method input to be changed accordingly to except dir string as argument instead of absolute path to the CSV file.

def open_even_if_gzipped(filename):
    '''Input: filename as string
    Output: Read-only file object, undoing gzip compression if necessary'''
    try:
        plaintext_fd = gzip.open(filename)
        plaintext_fd.seek(1)
        plaintext_fd.seek(0)
    except IOError:
        plaintext_fd = open(filename)

    return plaintext_fd

def ccLogDataGrouper(filepath):
     accessPattern = re.compile('^(?P<id>[^,]*),(?P<url>[^,]*),(?P<searchengine>[^,]*),(?P<count>[^,]*),(?P<date>[^ ]*) (?P<time>[^,]*),(?P<jurcode>[^,]*),(?P<lic>[^,]*),(?P<version>[^,]*),(?P<juris>.*)\r$') #regex to get the useful parts

     if filepath.endswith('.csv'):
          logfile = open_even_if_gzipped(filepath)
          for line in logfile:
               compare = accessPattern.match(line) #Match the stats file data to the regex
               if compare is None: # then the regex failed, and the input data was invalid.
                    print line
                    raise ValueError
               else: # Extract the relevant data
                    this_datum = compare.groupdict()
                    # fix up count to actually be an integer
                    this_datum['count'] = int(this_datum['count'])
                    # slide it onto the end of our growing list
                    data_from_logs.append(this_datum)
          logfile.close()

     # reorganize the data from the logs to be grouped by jurisdiction
     grouped_by_juris = {}
     # for me, "grouped by" means a dictionary where the key is the juris and the value
     # is a list of these data dictionaries

     for datum in data_from_logs:
        # each datum has: count, lic, version, juris, jurcode

        # For each datum we pulled out of the logs,
        # it in this dictionary whose keys are the "juris" 
        my_juris = datum['juris']

        if my_juris not in grouped_by_juris:
            grouped_by_juris[my_juris] = []
        grouped_by_juris[my_juris].append(datum)

     # Now that they are grouped, we can e.g. generate the sums
     juris_sums = {}
     for juris in grouped_by_juris:
        juris_sums[juris] = sum([datum['count'] for datum in grouped_by_juris[juris]])

     print juris_sums

# ADD ME: Also add logic to sub-group by license-type within jurisdiction grouping.
# ADD ME: System arguments for search engine and stat file type (linkback or api)

def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'You need to pass me exactly one CC CSV file as an argument.'
        print >> sys.stderr, 'You can find one here: http://labs.creativecommons.org/~cronuser/csv-dumps/2006-06-23/00:00:00/linkbacks-daily-Yahoo.csv'
        sys.exit(1)

    ccLogDataGrouper(sys.argv[1])

if __name__ == '__main__':
    main()
