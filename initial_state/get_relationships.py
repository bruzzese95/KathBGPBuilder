#!/usr/bin/env python

import json



def get_relationships():
	relationships = json.load(open("relationships.json", "r"))
	relationship_set = set()
	for relation in relationships["relationships"]:
		relationship_set.add((relation["asn"][0], relation["asn"][1], relation["type"], relation["special"]))
	return relationship_set

def get_customer(asn, dictionary):
	customer = set()
	for tupla in dictionary:
		if tupla[0] == asn and tupla[2] == "transit":
			customer.add(tupla[1])
	return customer
