# Implicit Paradigm Shifts and the Ship of Language Models

This repo presents the code for the analysis in [*What We Talk about When We Talk about LMs: Implicit Paradigm Shifts and the Ship of Language Models*](https://arxiv.org/abs/2407.01929) (To appear at NAACL 2025).

> **Abstract**: The term Language Models (LMs) as a time-specific collection of models of interest is constantly reinvented, with its referents updated much like the *Ship of Theseus* replaces its parts but remains the same ship in essence.
In this paper, we investigate this *Ship of Language Models* problem, wherein scientific evolution takes the form of continuous, implicit retrofits of key *existing* terms. We seek to initiate a novel perspective of scientific progress, in addition to the more well-studied emergence of *new* terms.
To this end, we construct the data infrastructure based on recent NLP publications.
Then, we perform a series of text-based analyses toward a detailed, quantitative understanding of the use of Language Models as a term of art. 
Our work highlights how systems and theories influence each other in scientific discourse, and we call for attention to the transformation of this Ship to which we all are contributing.

## Getting started

Our code is organized mainly as `.ipynb` notebooks for convenient, plug-and-play replication of the data analysis and visualization in our work. Specifically, the code contains several major modules:
- Data: 
	- **`/data`**: Data files on which the analysis code runs. [Download the zipped data from this link](https://drive.google.com/file/d/17unm6hT0wp_YWKi5WCm6DJfi9E7Bbsxs/view?usp=sharing) and extract the `/data` folder, which contains the raw (ending with '_overallLM.json)' and processed (ending with '_extracted_full.json') data from the 10 conferences covered in our work.
	- **`/model dependency`**: The key results of the human-AI model name detection module.
		 - **`model_merge_lookup.json`**: A key data structure of model names and their dependencies.
		 - **`stopword_lookup.json`**: A collection of stopwords discarded during human validation.
	- **`/fig`**: The figures produced by the analysis code (as well as files for post-processing), in correspondence with the paper content.
- Pre-processing Code:
	- **`acl_anthology_data_collection.ipynb`**: *(To be uploaded)* The script for crawling the anthology by available paper IDs.
	- **`extract_text_and_sections.ipynb`**: PDF-to-text scanning and post-processing of the extracted text.
- Analysis/Functional Code: 
	- **`data_analysis.ipynb`**: The central part of the code that produces all the figures and data. The notebook contains various modules that respectively corresponds to the different experiments.
	- **`util.py`**: A code base for the fundamental construction of model dictionaries.

To replicate the analysis in our work, obtain the data folders and code as described, have them in the same directory, and run `data_analysis.ipynb`.

## To-do List
- ~~Link to the data~~ *(completed)*
- Cleaning and uploading the raw data script
- Adding more comments and reader-friendly features for adaptation to the scripts
- Add more info and the FAQs to README
- Add a requirements.txt?

## FAQs
*(TBD)*

## Citation
*(This will be replaced by a formal ACL Anthology bibtex entry when it's published. For now, please use the following preprint to cite our work:)*

> @article{zhu2024we, \
  title={What We Talk About When We Talk About LMs: Implicit Paradigm Shifts and the Ship of Language Models}, \
  author={Zhu, Shengqi and Rzeszotarski, Jeffrey M}, \
  journal={arXiv preprint arXiv:2407.01929}, \
  year={2024} \
}
