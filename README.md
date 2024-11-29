# CiteMeMaybe

**CiteMeMaybe** is a Python script designed to extract the number of times authors of a paper cite themselves in their own work.

## Requirements
- Python 3.10+
- Libraries: 
  - `stanza`: For natural language processing to extract author and citation information.
  - `pymupdf4llm`: For working with PDF documents (to extract references from papers in PDF format).

### `requirements.txt`
The `requirements.txt` should contain the following dependencies:

```
stanza
pymupdf4llm
```

You can install them manually if preferred:
```bash
pip install stanza pymupdf4llm
```


## Usage
To run the script and analyse self-citations in a paper, simply run the following command:

```bash
python citememaybe.py --data_dir ./path/to/papers
```

The script will convert the pdf files in the specified directory to a markdown representation, extract the authors of the paper and then count the number of self-citations. The results will be saved to a csv in your working directory called `self_citation_report.csv`.

An example report and the analysed papers is given in `data`.