import os
import sys

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


my_as = str(sys.argv[2])
my_as_int = int(sys.argv[2])

my_as_complete.remove(my_as_int)

peers = set()
customers = set()
providers = set()


with open(str(sys.argv[1])) as f:
	for line in f:
		if line[0] == '#':
			continue
		else:
			split = line.split("|")
			for asn in my_as_complete:
				if my_as in split and str(asn) in split:
					if split[-2] == "0":
						peers.add(asn)
					elif split[0] == str(asn):
						providers.add(asn)
					elif split[1] == str(asn):
						customers.add(asn)
print("List of peers: ", end=" ")
if len(peers) != 0:
	print(peers)
else:
	print("{}")
print()
print("List of customers: ", end=" ")
if len(customers) != 0:
	print(customers)
else:
	print("{}")
print()
print("List of providers: ", end=" ")
if len(providers) != 0:
	print(providers)
else:
	print("{}")
