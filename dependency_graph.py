import os
import re
import argparse
from collections import defaultdict
from graphviz import Digraph

include_regex = re.compile('#include\s+["<"](.*)[">]')
valid_extensions = ['.c', '.cc', '.cpp', '.h', '.hpp']

def normalize(path):
	""" Return the name of the node that will represent the file at path. """
	filename = os.path.basename(path)
	end = filename.rfind('.')
	end = end if end != -1 else len(filename)
	return filename[:end]

def get_extension(path):
	""" Return the extension of the file targeted by path. """
	return path[path.rfind('.'):]

def find_all_files(path, recursive=True):
	""" 
	Return a list of all the files in the folder.
	If recursive is True, the function will search recursively.
	"""
	files = []
	for entry in os.scandir(path):
		if entry.is_dir() and recursive:
			files += find_all_files(entry.path)
		elif get_extension(entry.path) in valid_extensions:
			files.append(entry.path)
	return files

def find_neighbors(path):
	""" Find all the other nodes included by the file targeted by path. """
	f = open(path)
	try:
		code = f.read()
	except:
		print("ERROR - Could not parse file: ")
		print(path)
	return [normalize(include) for include in include_regex.findall(code)]

def create_graph(folder, create_cluster):
	""" Create a graph from a folder. """
	# Find nodes and clusters
	files = find_all_files(folder)
	folder_to_files = defaultdict(list)
	for path in files:
		folder_to_files[os.path.dirname(path)].append(path)
	nodes = {normalize(path) for path in files}
	# Create graph
	graph = Digraph()
	# Find edges and create clusters
	for folder in folder_to_files:
		with graph.subgraph(name='cluster_{}'.format(folder)) as cluster:
			for path in folder_to_files[folder]:
				node = normalize(path)
				if create_cluster:
					cluster.node(node)
				else:
					graph.node(node)
				neighbors = find_neighbors(path)
				for neighbor in neighbors:
					if neighbor != node and neighbor in nodes:
						graph.edge(node, neighbor)
	return graph

def find_cycles(node, neigbours_list):
	pass
	#out = []
	#for neigbor in neigbours_of_nodes:
	#	if neigbor == node


def create_graph_bidirectional(folder, create_cluster):
	""" Create a graph from a folder. """
	# Find nodes and clusters
	files = find_all_files(folder)
	folder_to_files = defaultdict(list)
	for path in files:
		folder_to_files[os.path.dirname(path)].append(path)
	nodes = {normalize(path) for path in files}
	# Create graph
	graph = Digraph()
	# Find edges and create clusters
	
	neigbours_of_nodes = {}

	# build neigbors list
	for folder in folder_to_files:
		with graph.subgraph(name='cluster_{}'.format(folder)) as cluster:
			for path in folder_to_files[folder]:					
				node = normalize(path)
				if not node in neigbours_of_nodes:
					neigbours_of_nodes[node] = []
				neigbours_list = []
				if create_cluster:
					cluster.node(node)
				else:
					graph.node(node)
				neighbors = find_neighbors(path)
				for neighbor in neighbors:
					if neighbor != node and neighbor in nodes:
						neigbours_list.append(neighbor)

				neigbours_of_nodes[node].append(neigbours_list)
	print(neigbours_of_nodes)
	
	for node in neigbours_list:
		find_cycles(node, neigbours_list)

	return graph

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('folder', help='Path to the folder to scan')
	parser.add_argument('output', help='Path of the output file without the extension')
	parser.add_argument('-f', '--format', help='Format of the output', default='pdf', \
		choices=['bmp', 'gif', 'jpg', 'png', 'pdf', 'svg'])
	parser.add_argument('-v', '--view', action='store_true', help='View the graph')
	parser.add_argument('-c', '--cluster', action='store_true', help='Create a cluster for each subfolder')
	args = parser.parse_args()
	graph = create_graph(args.folder, args.cluster)
	create_graph_bidirectional(args.folder, args.cluster)
	graph.format = args.format
	# On Windows: if youre not an admin, set:
	os.environ["PATH"] = os.environ["PATH"] + ";C:/Program Files (x86)/Graphviz2.38/bin/"
	#print(os.environ["PATH"])
	graph.render(args.output, cleanup=True, view=args.view)
