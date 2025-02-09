import json
from os import listdir
from os.path import isfile, join
from collections import Counter


def venueID2name(venue_index, mode='full'):
	n = venue_index.strip('-main').upper().split('.')
	if mode == 'full':
		return ' '.join(n)
	elif mode == 'brief':
		return '-'.join([w[0] if w[0] in ['A', 'E', 'N'] else w[2:] for w in n])
	else:
		return venue_index
	


def collect_model_names(paper_list_file):
	
	# Collect all the model names that appeared in some paper's abstract as a dict for model names
	
	# Input: 
	# paper_list: a json file (containing a list of dicts) generated in acl_anthology_data_collection
	
	# Output: 
	# model_names: a dict of all model names. Format: {'model_name': NUM} where NUM is the count of model_name

	with open(paper_list_file, 'r') as f1:
		paper_list = json.load(f1)

	model_names = {}

	for item in paper_list:
		mn_string = item['gpt_response']
		if mn_string != 'None':
			mn = mn_string.strip().split(',')
			for name in mn:
				if name not in model_names:
					model_names[name] = 0
				model_names[name] += 1

	return model_names


def merge_model_names_to_dict(path='data/', option='model_names'):

	# Retrieve all the model names dict and merge them to one dict, adding the count of the same model (Does not combine alias)

	# Input:
	# path: the file directory where all the relevant GPT-response json files are stored. Default: 'data/'
	# option: selection criteria for the files under path. maps to file name patterns in the dict below. Default: 'model_names', which corresponds to 'alt-justoverallLM'

	# Output:
	# full_model_names: the dict that includes the model names and count from all the files

	option2filename = {
		'model_names': 'overallLM'
	}

	f = []
	for file in listdir(path):
		if option2filename[option] in file:
			f.append(file)

	full_model_names = Counter({})
	for file in f:
		add_model_names = collect_model_names(join(path, file))
		full_model_names += Counter(add_model_names)

	return full_model_names


def update_matched_strings(file, path='data/', option='model_names', full_model_names=None, alias_file_path='model dependency/model_merge_lookup.json', by_chapter=None, precise_search=False, direct_write=True):

	# Update or generate the 'matched_names' dict attribute in a file based on full_model_names
	# should replace what was initially written in extract_experiment_sections

	# Input:
	# file: a file generated from extract_experiment_sections ('..._extracted_exp_secs.json') to be updated
	# full_model_names: if the full_model_names is given as input, the function will use it. Otherwise, the function will run merge_model_names_to_dict to generate it on the fly. Default: None
	# path: the file directory of the data files (and will be called by collect_model_names). Default: 'data/'
	# option: work mode of the function. Default: 'model_names'
			# 'model_names': call merge_model_names_to_dict to generate all the model names of interest and count them.
			# 'LM': search for the general terms of language models. current version: ['LLM', 'language model', 'PLM']
			# *Special case: If full_model_names is not none, it will override this variable and search the strings in full_model_names instead.
	# by_chapter: the title of the section/chapter of interest. If None, then search the full text. Default: None
	# direct_write: write to file directly if True; otherwise return the updated dict as the output of the function. Default: True

	# Output:
	# (if direct_write is True) None
	# (if direct_write if False) updated version of the dict from file

	with open(file, 'r', encoding='utf-8') as f:
		dataset = json.load(f)

	if full_model_names is None:
		if option == 'model_names':
			full_model_names = merge_model_names_to_dict(path, option)
			if alias_file_path is not None:
				_, alias_dict = import_model_dict(alias_file_path)
			else:
				alias_dict = []
		elif option == 'LM':
			full_model_names = ['language model', 'LLM', 'PLM', 'Language Model', "Language model", "language-model", "Language-Model"]
			alias_dict = {"language model": 'language model',
						'Language Model': 'language model',
						"Language model": 'language model',
						"language-model": 'language model',
						"Language-Model": 'language model',
						'LLM': 'LLM',
						'PLM': 'PLM'
						}
		else:
			print(f'Error: No work mode named "{option}". Check the "option" variable.')
			return

	substring_mapping = build_substring_mapping(full_model_names)

	for i in range(len(dataset)):
		dataset[i][f'matched_{option}'] = {}
		if dataset[i]['text'] is not None:
			for item in alias_dict.keys():
				if by_chapter is None:
					appear_count = dataset[i]['text'].count(item)
				elif by_chapter == '__REMOVE_REF__':
					appear_count = sum([dataset[i]['by_chapter'][k].count(item) for k in dataset[i]['by_chapter'].keys() if k!='References'])
				else:
					appear_count = 0
					if type(by_chapter) is str:
						by_chapter = [by_chapter]
					for c in by_chapter:
						if precise_search: # only when the query exactly matches some chapter name
							if len(dataset[i]['by_chapter'].keys())>0 and c in dataset[i]['by_chapter']:
								appear_count = dataset[i]['by_chapter'][c].count(item)
						else: # all chapters that contain the query
							for cand in dataset[i]['by_chapter']:
								if c in cand:
									appear_count += dataset[i]['by_chapter'][cand].count(item)
							
				if appear_count > 0:
					target_key = item #(deprecated) previous version: alias_dict[item]
					if target_key not in dataset[i][f'matched_{option}']:
						dataset[i][f'matched_{option}'][target_key] = 0
					dataset[i][f'matched_{option}'][target_key] += appear_count
			dataset[i][f'cleaned_no-alias-merge_matched_{option}'] = correct_string_counts(dataset[i][f'matched_{option}'], substring_mapping)
			dataset[i][f'matched_{option}'] = combine_alias(dataset[i][f'matched_{option}'], alias_dict)
			dataset[i][f'cleaned_matched_{option}'] = combine_alias(dataset[i][f'cleaned_no-alias-merge_matched_{option}'], alias_dict)


		# remove repetitions by calling 
		# save as another dict [f'cleaned_matched_{option}']
		

	if direct_write:
		with open(file, 'w', encoding='utf-8') as f1:
			json.dump(dataset, f1, indent=4)
	else:
		return dataset


def import_model_dict(file_path='model dependency/model_merge_lookup.json', include_variations=True):

	# Import and process model names from a model_merge_lookup.json -like file.
	# If no such file is given as input, fetch the default dict by running merge_model_names_to_dict on the fly

	# Input:
	# file_path: the file path and name of a model_merge_lookup.json -like file.
	# include_variations: a boolean value. If True, the alias will collect from both ['alias'] and ['variations']. If False, only collect from ['alias'].

	# model_merge_lookup.json contains a dict of model names and their metadata (alias, variations, dependency).
	# Example format:
	# "LLaMA": {
    #	"alias": ["LLaMA", "LlaMA", "Llama", "LLaMa"],
    #	"variations": ["LLaMA-13B", "Llama-2"],
    #	"dep": "LLaMA",
    #	"ref": "https://github.com/facebookresearch/llama"
    # }

	if file_path is not None:
		with open(file_path, 'r', encoding='utf-8') as f1:
			dataset = json.load(f1)
		#print(dataset)

		# We first implement the basic functionality of merging aliases.
		reverse_dict = {}
		for model in dataset.keys():
			for name in dataset[model]['alias']:
				assert name not in reverse_dict # A model name (alias) shall not belong to more than one model
				reverse_dict[name] = model
			if include_variations:
				for name in dataset[model]['variations']:
					assert name not in reverse_dict
					reverse_dict[name] = model
	else:
		res = merge_model_names_to_dict()
		reverse_dict = {k:k for k in res.keys()}

	return dataset, reverse_dict


def combine_alias(model_names, reverse_dict):
	
	# Based on a reverse_dict, combine the same items in model_names to form a new dict.
	# The new dict's keys will be a subset of the keys of reverse_dict.

	# Input:
	# model_names: a model_names -like or ['matched_model_names'] dict containing pairs of model names and counts
	# reverse_dict: a mapping dict from aliases to the main model name generated by import_model_dict

	# Output:
	# combined_model_names: the combined dict of model names where aliases are collected into the same bin.

	combined_model_names = {}

	for name in model_names.keys():
		if name in reverse_dict: # Discard the models that have not been mapped
			if reverse_dict[name] not in combined_model_names:
				combined_model_names[reverse_dict[name]] = 0
			combined_model_names[reverse_dict[name]] += model_names[name]

	return Counter(combined_model_names)


def build_substring_mapping(model_names):

	# Given a full model_names dict over all models of interest,
	# find and arrange all the superstrings of every model name.
	# This is used together with correct_string_counts to remove repetitions during counting (e.g. RoBERTa contains BERT).

	# Input:
	# model_names: a model_names dict. This function should only be run on the full collection of model names (to capture all superstrings).

	# Output:
	# substring_mapping: a dict where the keys are the model names and the values are lists of superstrings for each model name. Both the keys and values are sorted from long to short.

	substring_mapping = {}
	sorted_keys = sorted(model_names, key=len, reverse=True)

	for i in range(len(sorted_keys)):
		key = sorted_keys[i]
		substring_mapping[key] = []
		for longer_key in sorted_keys[:i]:
			if key in longer_key:
				substring_mapping[key].append(longer_key)

	return substring_mapping


def correct_string_counts(string_counts, substring_mapping):

	# Given a model_name -like dict that maps model names to counts,
	# deduct repetitive counts from its superstrings (recorded in substring_mapping)
	# (operates from the longest string to the shortest, following a DP-like algorithm)

	# Extend the input dict to contain all model names in substring_mapping
	corrected_counts = {key: string_counts.get(key, 0) for key in substring_mapping.keys()}

	for key, superstrings in substring_mapping.items():
		for superstring in superstrings:
			corrected_counts[key] -= corrected_counts[superstring]

	shortened_corrected_counts = {key: corrected_counts[key] for key in corrected_counts.keys() if corrected_counts[key]>0}

	return shortened_corrected_counts

