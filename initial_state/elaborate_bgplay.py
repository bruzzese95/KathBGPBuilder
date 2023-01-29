#!/usr/bin/env python

import os
import json
from collections import Counter
from pprint import pprint
from string import ascii_uppercase
import get_prefixes
import get_relationships as relation


data = json.load(open("data.json", "r"))

BAD_AS = 8342
TARGET_AS = 13414

tuple_configuration = set()

my_victims = {8359: {'13-195.208.208.30', '12-80.81.192.78'}, 28917: {'13-195.208.208.147'}, 
 57695: {'01-195.66.227.120'},  8660: {'10-217.29.66.233'}}

debug_as_list = {
	21232,
	59414,
	13414,
	13030,
	1299,
	22652,
	8359,
	8342,
	1267,
	8660
}

compare_AS = { 6720, 8447, 13414, 8359, 8342, 8607, 2914, 9304, 15435, 19151, 21232, 13030, 22652, 1299,
8660, 1267, 25091, 28917, 41095, 3356, 51185, 56665, 57695, 60068, 59414, 59605, 137409, 199524 }

ip_third_counter = 0
ip_fourth_counter = 4



def write_daemons_file(path):
	daemons_path = os.path.join(path, "daemons")
	f = open(daemons_path, "w")
	f.write("zebra=yes\nbgpd=yes\nospfd=no\nospf6d=no\nripd=no\nripngd=no")
	f.close()


def create_paths():
	paths = set()
	for event in data["data"]["events"]:
		if event["type"] == "A" and event["attrs"]["path"][-1] == BAD_AS:
			paths.add(tuple(event["attrs"]["path"]))
	return paths


def create_victims_dictionary(data):
	victims_dictionary = dict()
	for event in data["data"]["events"]:
		if event["type"] == "A" and event["attrs"]["path"][-1] == BAD_AS:
			key_as = event["attrs"]["path"][0]
			victims_dictionary.setdefault(key_as, set())
			victims_dictionary[key_as].add(event["attrs"]["source_id"])
	return victims_dictionary


def create_counter_ases():
	ases = Counter()
	for source in data["data"]["sources"]:
		ases[source["as_number"]] += 1
	return ases


def create_links_my_victims(data):
	links = set()
	for state in data["data"]["initial_state"]:
		path = state["path"]
		for asn in victims_dictionary:
			if path[0] == asn and state["source_id"] in victims_dictionary[asn]:
				for i in range(0, len(path)-1):
					if path[i] == path[i+1]:
						continue
					pair = (
						min(path[i], path[i+1]),
						max(path[i], path[i+1])
						)
					links.add(pair)
	return links

def create_links_debug(paths):
	links = set()
	for path in paths:
		for i in range(0, len(path)-1):
			if path[i] == path[i+1]:
				continue
			pair = (
				min(path[i], path[i+1]),
				max(path[i], path[i+1])
				)
			links.add(pair)
	return links

def create_links_victims_dictionary(data):
	links = set()
	for state in data["data"]["initial_state"]:
		path = state["path"]
		for asn in victims_dictionary:
			if path[0] == asn and state["source_id"] in victims_dictionary[asn]:
				for i in range(0, len(path)-1):
					if path[i] == path[i+1]:
						continue
					pair = (
						min(path[i], path[i+1]),
						max(path[i], path[i+1])
						)
					links.add(pair)
	return links

def create_links_v2_all_victims():
	links = set()
	for path in paths:
		for i in range(len(path)-1):
			pair = (path[i], path[i+1])
			links.add(pair)
	return links

def create_links_v2_my_victims():
	links = set()
	paths_cut = set()
	for path in paths:
		for asn in my_as_complete:
			if asn in path and asn != 8359 and asn != 8342:
				paths_cut.add(path)
				break
	for path in paths_cut:
		for i in range(len(path)-1):
			pair = (
					min(path[i], path[i+1]),
					max(path[i], path[i+1])
				)
			links.add(pair)
	return links


def create_my_as_complete(links):
	my_as_complete = set()
	for pair in links:
		my_as_complete.add(pair[0])
		my_as_complete.add(pair[1])
	for victim in victims_dictionary:
		if victim not in my_as_complete:
			my_as_complete.add(victim)
	my_as_complete.add(BAD_AS)
	my_as_complete.add(TARGET_AS)
	return my_as_complete


def debug_create_interface_dictionary(relationships, complete_set):
	interface_dictionary = dict()
	for asn in complete_set:
		interface_dictionary[asn] = 0
	for relation in relationships:
		interface_dictionary[relation[0]] += 1
		interface_dictionary[relation[1]] += 1
	return interface_dictionary


def print_values():
	print("Relationships: ")
	pprint(relationships)
	print()
	print("AS complete list: ")
	pprint(debug_complete_set)
	print()
	print("Interface dictionary: ")
	pprint(interface_dictionary)
	print()
	print("Pair interfaces:")
	pprint(pair_interface_tuples)
	print()
	print("Tuple configuration:")
	pprint(tuple_configuration)
	print()
	print("Ip network tuples:")
	pprint(ip_network_tuples)

def get_lab_directory():
	current_directory = os.getcwd()
	lab_directory = os.path.join(current_directory, "lab_twitter_hijack")
	return lab_directory


def create_lab_directory():
	lab_directory = get_lab_directory()
	if not os.path.exists(lab_directory):
		os.makedirs(lab_directory)


def clean_startup_files(node):
	startup_path = os.path.join(get_lab_directory(), "as"+str(node)+".startup")
	f = open(startup_path, "w")
	f.close()


def create_configuration_files(complete_set, pair_interface_tuples, prefixes_dict, interface_dictionary):
	global ip_third_counter, ip_fourth_counter, TARGET_AS

	for node in complete_set:

		#Create the startup file path
		startup_path = os.path.join(get_lab_directory(), "as"+str(node)+".startup")

		clean_startup_files(node)

		#Create the /etc/quagga path
		node_directory = os.path.join(get_lab_directory(), r"as"+str(node)+"/etc/quagga")
		if not os.path.exists(node_directory):
			os.makedirs(node_directory)


		#Create and write the /etc/quagga/daemons file
		write_daemons_file(node_directory)


	for element in pair_interface_tuples:
		startup_path_first = os.path.join(get_lab_directory(), "as"+str(element[0])+".startup")
		interface_number_first = element[2]
		ip_fourth_counter += 1
		ip_address_first = "11.0."+str(ip_third_counter)+"."+str(ip_fourth_counter)
		ip_fourth_counter += 1

		startup_path_second = os.path.join(get_lab_directory(), "as"+str(element[1])+".startup")
		interface_number_second = element[3]
		ip_address_second = "11.0."+str(ip_third_counter)+"."+str(ip_fourth_counter)
		ip_fourth_counter += 2


		write_ip_address_30(startup_path_first, ip_address_first, interface_number_first)
		tuple_configuration.add((element[0], interface_number_first, ip_address_first))
		

		write_ip_address_30(startup_path_second, ip_address_second, interface_number_second)
		tuple_configuration.add((element[1], interface_number_second, ip_address_second))

	del prefixes_dict[TARGET_AS]

	prefixes_dict[TARGET_AS] = [ip_target]

	for asn in prefixes_dict:
		startup_path = os.path.join(get_lab_directory(), "as"+str(asn)+".startup")
		prefixes_list1 = prefixes_dict[asn][0].split("/")
		ip_1 = prefixes_list1[0][:-1]
		ip_tot1 = ip_1+"1/"+prefixes_list1[1]

		if asn == TARGET_AS:
			write_ip_address(startup_path, ip_tot1, interface_dictionary[asn])
		else:
			prefixes_list2 = prefixes_dict[asn][1].split("/")
			ip_2 = prefixes_list2[0][:-1]
			ip_tot2 = ip_2+"1/"+prefixes_list2[1]
			write_ip_address(startup_path, ip_tot1, interface_dictionary[asn])
			write_ip_address(startup_path, ip_tot2, interface_dictionary[asn]+1)

	write_zebra_start(complete_set)


def write_ip_address_30(startup_path, ip_address, interface_number):
	f = open(startup_path, "a")
	f.write("ip addr add "+ip_address+"/30 dev eth"+str(interface_number)+"\n")
	f.close()

def write_ip_address(startup_path, ip_address, interface_number):
	f = open(startup_path, "a")
	f.write("ip addr add "+ip_address+" dev eth"+str(interface_number)+"\n")
	f.close()


def write_zebra_start(complete_set):
	for node in complete_set:
		startup_path = os.path.join(get_lab_directory(), "as"+str(node)+".startup")
		f = open(startup_path, "a")
		f.write("/etc/init.d/zebra start")
		f.close()



def create_bgpd_file(complete_set, relationships):
	#Create bgpd.conf file
	for node in complete_set:
		node_directory = os.path.join(get_lab_directory(), r"as"+str(node)+"/etc/quagga")
		bgpd_path = os.path.join(node_directory, "bgpd.conf")
		f = open(bgpd_path, "w")
		write_bgpd_file(node, f, tuple_configuration, pair_interface_tuples, relationships)
		f.close()


def write_bgpd_file(node, f, tuple_configuration, pair_interface_tuples, relationships):
	neighbors = find_neighbors(node, relationships)
	f.write("!\nhostname bgpd\npassword zebra\nenable password zebra\n!\n")
	f.write("router bgp "+str(node)+"\n!\n")

	if node == 13414:
		f.write("network "+ip_target+"\n!\n")
	else:
		write_network_bgpd(f, prefixes_dict, node)

	node_eth = None
	AS_eth = None
	node_ip_address = None
	AS_ip_address = None
	prefixes_in = set()
	has_filter_out = False


	for AS in neighbors:

		for pair in pair_interface_tuples:
			if node in pair and AS in pair:

				#Assign eth value to each node
				if node == pair[0]:
					node_eth = pair[2]
					AS_eth = pair[3]
					break
				else:
					AS_eth= pair[2]
					node_eth = pair[3]
					break
			else:
				continue
		for element in tuple_configuration:
			if node == element[0] and node_eth == element[1]:
				node_ip_address = element[2]
			elif AS == element[0] and AS_eth == element[1]:
				AS_ip_address = element[2]

		f.write("neighbor "+str(AS_ip_address)+" remote-as "+str(AS)+"\n")
		f.write("neighbor "+str(AS_ip_address)+" description Router of AS"+str(AS)+"\n")


		for relation in relationships:
			if AS in relation and node in relation:
				if  node == 8359 and AS == 8342:
					f.write("neighbor "+str(AS_ip_address)+" filter-list filterIn"+str(AS)+" in\n!\n")
					prefixes_in.add(AS)
					break
				if relation[3] == "true" and BAD_AS not in relation:
					f.write("!\n")
					break
				if relation[2] == "peering":
					f.write("neighbor "+str(AS_ip_address)+" prefix-list filterIn"+str(AS)+" in\n")
					f.write("neighbor "+str(AS_ip_address)+" prefix-list filterOut out\n!\n")
					has_filter_out = True
					prefixes_in.add(AS)
					break
				if relation[2] == "transit" and relation[1] == node:
					f.write("neighbor "+str(AS_ip_address)+" prefix-list filterOut out\n!\n")
					has_filter_out = True
					break
				if relation[2] == "transit" and relation[0] == node:
					f.write("neighbor "+str(AS_ip_address)+" prefix-list filterIn"+str(AS)+" in\n!\n")
					prefixes_in.add(AS)
					break


	for ASN in prefixes_in:
		if node == 8359 and ASN == 8342:
			f.write("ip as-path access-list filterIn"+str(BAD_AS)+" permit ^"+str(BAD_AS)+"$\n!\n")
		elif ASN != 13414:
			f.write("ip prefix-list filterIn"+str(ASN)+" permit "+str(prefixes_dict[ASN][0])+"\n")
			f.write("ip prefix-list filterIn"+str(ASN)+" permit "+str(prefixes_dict[ASN][1])+"\n")
		
			customers = return_customers(ASN)
			if len(customers) > 0:
				for customer in customers:
					f.write("ip prefix-list filterIn"+str(ASN)+" permit "+str(prefixes_dict[customer][0])+"\n")
					f.write("ip prefix-list filterIn"+str(ASN)+" permit "+str(prefixes_dict[customer][1])+"\n")
			f.write("!\n")
		else:
			f.write("ip prefix-list filterIn"+str(TARGET_AS)+" permit "+str(ip_target)+"\n!\n")

	if has_filter_out:
		if node != 13414:
			f.write("ip prefix-list filterOut permit "+str(prefixes_dict[node][0])+"\n")
			f.write("ip prefix-list filterOut permit "+str(prefixes_dict[node][1])+"\n")

			customers = return_customers(node)
			if len(customers) > 0:
				for customer in customers:
					f.write("ip prefix-list filterOut permit "+str(prefixes_dict[customer][0])+"\n")
					f.write("ip prefix-list filterOut permit "+str(prefixes_dict[customer][1])+"\n")
				f.write("!\n")
			else:
				f.write("!\n")
		elif node == 13414:
			f.write("ip prefix-list filterOut permit "+str(ip_target)+"\n!\n")
		

	f.write("log file /var/log/zebra/bgpd.log\n!\ndebug bgp\ndebug bgp events\ndebug bgp filters\ndebug bgp fsm\ndebug bgp keepalives\ndebug bgp updates\n!\n")
	f.close()


def return_customers(node):
	customers = set()
	for relation in relationships:
		if relation[2] == "transit" and relation[0] == node:
			customers.add(relation[1])
	return customers


def write_network_bgpd(f, prefixes_dict, node):
	f.write("network "+prefixes_dict[node][0]+"\n")
	f.write("network "+prefixes_dict[node][1]+"\n!\n")


def find_ip_address(node, interface, tuple_configuration):
	for element in tuple_configuration:
		if node == element[0] and interface == element[1]:
			return element[2]


def find_neighbors(node, relationships):
	neighbors = set()
	for relation in relationships:
		if node in relation:
			neighbors.add(relation[0])
			neighbors.add(relation[1])
	if len(neighbors) > 0:
		neighbors.remove(node)
	return neighbors


def assign_prefixes_conf(prefixes_dict, interface_dictionary):
	ch = 'a'
	lab_conf_path = os.path.join(get_lab_directory(), "lab.conf")
	f = open(lab_conf_path, "a")
	for asn in prefixes_dict:
		f.write("as"+str(asn)+"["+str(interface_dictionary[asn])+"]=\""+ch+"\"\n")
		f.write("as"+str(asn)+"pc1[0]=\""+ch+"\"\n")
		ch = chr(ord(ch) + 1)

		write_startup_pc(asn, prefixes_dict, 1)

		if asn == TARGET_AS:
			ch = chr(ord(ch) + 1)
		else:
			f.write("as"+str(asn)+"["+str(interface_dictionary[asn]+1)+"]=\""+ch+"\"\n")
			f.write("as"+str(asn)+"pc2[0]=\""+ch+"\"\n")
			write_startup_pc(asn, prefixes_dict, 2)
			ch = chr(ord(ch) + 1)

	f.close()

def write_startup_pc(asn, prefixes_dict, number):
	startup_path = os.path.join(get_lab_directory(), "as"+str(asn)+"pc"+str(number)+".startup")
	g = open(startup_path, "w")
	ip = prefixes_dict[asn][number-1]
	ip_split = ip.split("/")
	g.write("ip addr add "+ip_split[0][:-1]+"2/"+ip_split[1]+" dev eth0\n")
	g.write("ip route add default via "+ip_split[0][:-1]+"1")
	g.close()
	


def create_pair_interface_list_and_write_lab_conf(relationships, interface_dictionary):
	pair_interface_tuples = set()
	using_dictionary = interface_dictionary.copy()
	lab_conf_path = os.path.join(get_lab_directory(), "lab.conf")
	f = open(lab_conf_path, "w")
	ch = 'A'
	for relation in relationships:
		f.write("as"+str(relation[0])+"["+str(using_dictionary[relation[0]]-1)+"]=\""+ch+"\"\n")
		f.write("as"+str(relation[1])+"["+str(using_dictionary[relation[1]]-1)+"]=\""+ch+"\"\n")
		pair_interface_tuples.add((relation[0], relation[1], using_dictionary[relation[0]]-1, using_dictionary[relation[1]]-1))
		ch = chr(ord(ch) + 1)
		using_dictionary[relation[0]] -= 1
		using_dictionary[relation[1]] -= 1
	f.close()
	return pair_interface_tuples


def create_ip_network_tuples(tuple_configuration, pair_interface_tuples):
	global ip_third_counter

	pair_ip_network_tuples = set()

	for pair in pair_interface_tuples:
		ip_network = None
		for element in tuple_configuration:
			if pair[0] == element[0] and element[1] == pair[2]:
				last_of_ip = get_last_of_ip(element[2])
				if last_of_ip % 2 == 0:
					ip_network = "11.0."+str(ip_third_counter)+"."+str(last_of_ip - 2)+"/30"
					break
				else:
					ip_network = "11.0."+str(ip_third_counter)+"."+str(last_of_ip - 1)+"/30"
					break
		pair_ip_network_tuples.add((pair[0], pair[1], ip_network))
	return pair_ip_network_tuples

def get_last_of_ip(ip_address):
	last = ip_address[-3:]
	if "." in last:
		last = ip_address[-2:]
		if "." in last:
			last = ip_address[-1]
	return int(last)

def get_ip_target():
	return data["data"]["resource"]


def link_union(link1, link2):
	link_complete = link1.copy()
	for pair in link2:
		if pair in link_complete:
			continue
		else:
			link_complete.add(pair)
	return link_complete


def debug_create_victims_set(debug_paths):
	victims = set()
	for path in debug_paths:
		for asn in path:
			victims.add(asn)
	return victims


def debug_create_initial_paths(debug_paths):
	initial_paths = []
	for state in data["data"]["initial_state"]:
		path = state["path"]
		path_set = set(path)
		for bad_path in debug_paths:
			i = bad_path.index(8359)
			asn = set()
			for index in range(0, i):
				asn.add(bad_path[index])
			if asn.issubset(path_set):
				initial_paths.append(path)
	initial_paths = set(tuple(i) for i in initial_paths)
	return initial_paths

def debug_union_victims(set1, set2):
	final_set = set1.copy()
	for asn in set2:
		final_set.add(asn)
	return final_set

def create_target_startup():
	startup_path = os.path.join(get_lab_directory(), "as"+str(TARGET_AS)+"pc1.startup")
	f = open(startup_path, "w")
	ip_list = ip_target.split("/")
	ip_addr = ip_list[0][:-1]
	f.write("ip addr add "+ip_addr+"2/"+ip_list[1]+" dev eth0")
	f.write("ip route add default via "+ip_addr+"1/"+ip_list[1])
	f.close()




#Get the IP target of the attack (104.244.42.0/24 in the case of Twitter Hijack)
ip_target = get_ip_target()

#Selected bad path for this experiment
debug_bad_paths = {(59414, 13030, 8359, 8342), (8660, 1267, 8359, 8342), (22652, 8359, 8342), (21232, 13030, 8359, 8342)}

debug_good_paths = debug_create_initial_paths(debug_bad_paths)

#Selected victims for this experiment
debug_bad_as_set = debug_create_victims_set(debug_bad_paths)
debug_good_as_set = debug_create_victims_set(debug_good_paths)
debug_complete_set = debug_union_victims(debug_good_as_set, debug_bad_as_set)

relationships = relation.get_relationships()


#Get the dictionary with the prefixes of all ASs
prefixes_dict = get_prefixes.peval(debug_complete_set)


interface_dictionary = debug_create_interface_dictionary(relationships, debug_complete_set)

#Create lab directory
create_lab_directory()


#Create lab.conf and pair interface list
pair_interface_tuples = create_pair_interface_list_and_write_lab_conf(relationships, interface_dictionary)

#Create and write startup files, /etc/quagga directory, /etc/quagga/daemons files, /etc/quagga/bgpd.conf files, tuple configuration
create_configuration_files(debug_complete_set, pair_interface_tuples, prefixes_dict, interface_dictionary)

ip_network_tuples = create_ip_network_tuples(tuple_configuration, pair_interface_tuples)

create_bgpd_file(debug_complete_set, relationships)

assign_prefixes_conf(prefixes_dict, interface_dictionary)



print_values()

print()
print("Prefixes dictionary:")
pprint(prefixes_dict)
print()
