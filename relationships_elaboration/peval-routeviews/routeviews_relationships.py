import sys
from pprint import pprint

upstreams = set()
upstreams_dict = dict()

my_as_complete = {1267,
 1299,
 2914,
 3356,
 6720,
 8342,
 8359,
 8447,
 8607,
 8660,
 9304,
 12389,
 13030,
 13414,
 15435,
 19151,
 21232,
 22652,
 25091,
 28917,
 33891,
 41095,
 51185,
 56665,
 57695,
 59414,
 59605,
 60068,
 137409,
 199524}


#my_as = "3356"
#my_as_int = 3356
my_as = str(sys.argv[1])
my_as_int = int(sys.argv[1])

my_as_complete.remove(my_as_int)

index_as = 0


with open('as'+my_as+'.txt') as f:
    for line in f:
        splitted = line.split()
        if len(splitted) > 0 and splitted[0].isnumeric() and len(splitted) >= 2 and my_as in splitted:
            if my_as+',' in splitted:
                index_as = splitted.index(my_as+',')
            else:
                index_as = splitted.index(my_as)
            upstream = int(splitted[index_as-1])
            if upstream in my_as_complete:
                upstreams.add(upstream)
                if upstream not in upstreams_dict:
                    upstreams_dict[upstream] = 1
                else:
                    upstreams_dict[upstream] += 1


print(my_as+" - Upstreams: ", end=" ")
pprint(upstreams_dict)
