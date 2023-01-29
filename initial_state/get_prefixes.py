#!/usr/bin/env python

import subprocess
from pprint import pprint
import ipaddr


asn_prefixes = dict()



def peval(my_as_list):
	cmd = "peval"
	outputlist = []
	for asn in my_as_list:
		counter = 1
		temp = subprocess.Popen([cmd, "as"+str(asn)], 
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT)
		stdout, stderr = temp.communicate()
		outputlist.append(str(stdout))
		lista = outputlist[0].split(",")
		for i in range(0, len(lista)):
			lista[i] = lista[i].strip()
		ip1 = ipaddr.IPNetwork(lista[counter])
		counter += 1
		ip2 = ipaddr.IPNetwork(lista[counter])
		while ip1.overlaps(ip2):
			counter += 1
			ip2 = ipaddr.IPNetwork(lista[counter])
		asn_prefixes[asn] = [str(ip1), str(ip2)]
		
		print("Overlaps "+str(ip1)+" and "+str(ip2)+"?")
		print(ip1.overlaps(ip2))

		outputlist = []
	return asn_prefixes
