# -*- coding: utf-8 -*-
import sys

count = []
license = []
version = []
juris = []
juriscode = []

groupedJuris = []
groupedJurisCode = []
groupedCount = []

### Consider Me: A CSV parser instead of crummy regex
### ADD ME: Additional code to identify which file to use as input when asked to grab the latest file, given the stats dir

"""     dirlist = [d for d in os.listdir(dir) if os.path.isdir(d)] #Uses the OS module to get a directory listing for the argument dir (folders only)
     dirlist.sort() #Sorts the directory listing
     latest = dirlist[len(dirlist)] #Grabs the latest folder."""

### Still need to navigate to the timestamp folder within and get hold of the relevant CSV. Method input to be changed accordingly to except dir string as argument instead of absolute path to the CSV file.

def ccLogDataGrouper(filepath):
     accessPattern = re.compile('^(?P<id>[^,]*),(?P<url>[^,]*),(?P<searchengine>[^,]*),(?P<count>[^,]*),(?P<date>[^ ]*) (?P<time>[^,]*),(?P<jurcode>[^,]*),(?P<lic>[^,]*),(?P<version>[^,]*),(?P<juris>.*)\r$') #regex to get the useful parts

     if filepath.endswith('.csv'):
          logfile = open(filepath, 'r')
          for line in logfile:
               compare = accessPattern.match(line) #Match the stats file data to the regex
               if compare is None:
                    print line
                    raise ValueError
               else: # Extract the relevant data
                    count.append(compare.groupdict()["count"])
                    license.append(compare.groupdict()["lic"])
                    version.append(compare.groupdict()["version"])
                    juris.append(compare.groupdict()["juris"])
                    juriscode.append(compare.groupdict()["jurcode"])
          logfile.close()

     counter = 0
     counterIncremented = 1 #To prevent out-of-bounds error, using counterIncremented instead of counter+1
### FIX ME: Still getting out of bound error, leading to ignoring of the last jurisdiction in the log
     temp = 0
     while counter < len(count): # Code to group the info by jurisdiction
          temp += int(count[counter])
          if juris[counter] != juris [counterIncremented]:
               groupedJuris.append(juris[counter])
               groupedJurisCode.append(juriscode[counter])
               groupedCount.append(temp)
               temp=0 
          counter += 1
          if counter == len(count):
               counterIncremented = counter
          else:
               counterIncremented = counter+1

# ADD ME: Also add logic to sub-group by license-type within jurisdiction grouping.
# ADD ME: System arguments for search engine and stat file type (linkback or api)

def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'You need to pass me exactly one CC CSV file as an argument.'
        print >> sys.stderr, 'You can find one here: http://labs.creativecommons.org/~paulproteus/stats/flickr/2008-06-23.csv'
        sys.exit(1)
    ccLogDataGrouper(sys.argv[1])

if __name__ == '__main__':
    main()
