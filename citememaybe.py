import re
import argparse
import stanza
import unicodedata
import pymupdf4llm

from pathlib import Path

MD_DIR = Path(Path.cwd(), "markdown")
MD_DIR.mkdir(exist_ok=True)

name_pattern = re.compile(r"^[A-Z][a-z]+ [A-Z][a-z]+", re.MULTILINE)


def parse_args():
    parser = argparse.ArgumentParser(description="Count self-citations")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to the set of papers (in PDF format) to be analysed")
    # parser.add_argument("--languages", type=str, nargs="+", default=["en", "el", "zh"], help="Languages to use for named entity recognition")
    parser.add_argument("--languages", type=str, nargs="+", default=["en"], help="Languages to use for named entity recognition")
    return parser.parse_args()


def extract_authors(md_text, languages):
    def extract_names(text):
        identified_names = set()
        for language in languages:
            stanza.download(language)
            nlp = stanza.Pipeline(language=language, processors="tokenize,ner", verbose=False)
            doc = nlp(text)
            names = [ent.text for sent in doc.sentences for ent in sent.ents if ent.type == "PERSON"]
            identified_names.update(names)

        return list(identified_names)

    authors = []

    md_text_lower = md_text.lower()
    md_text = md_text.replace("*", "")

    # Split text on abstract, introduction
    split_sections = ["abstract", "introduction"]
    for section in split_sections:
        section_idx = md_text_lower.find(section)
        if section_idx == -1:
            continue

        # Get content before section
        section_text = md_text[:section_idx]

        # Get authors
        authors = extract_names(section_text)

        # Normalise names
        authors = [unicodedata.normalize("NFC", name) for name in authors]

        # Split author names, keep only first and last name
        for i, author in enumerate(authors):
            split_name = author.split()
            first_name, last_name = split_name[0], split_name[-1]
            authors[i] = f"{first_name} {last_name}"

    return authors


def count_self_citations(md_text, authors):
    """ To do: improve this function to handle more complex cases
                and to avoid false positives
    """
    self_citation_counts = {author: 0 for author in authors}

    md_text_lower = md_text.lower()
    section_idx = md_text_lower.find("references")
    if section_idx == -1:
        return self_citation_counts
    
    references_text = md_text_lower[section_idx:]

    for author in authors:
        last_name = author.split()[-1]
        last_name = last_name.lower()
        regex = re.compile(rf"\b{last_name}\b")
        self_citation_counts[author] = len(regex.findall(references_text))

    return self_citation_counts


def write_results(citedmemaybe_report):
    csv_path = Path("self_citation_report.csv")
    with open(csv_path, "w") as csv_file:
        csv_file.write("paper,author,self_citations\n")
        for paper, author_counts in citedmemaybe_report.items():
            for author, count in author_counts.items():
                csv_file.write(f"{paper},{author},{count}\n")

    print("Results written to self_citation_report.csv")


def main(args):
    papers = Path(args.data_dir).rglob("*.pdf")

    citedmemaybe_report = {}

    for paper in papers:
        # Preprocess PDFs to markdown
        markdown_path = Path(MD_DIR, paper.stem + ".md")
        if markdown_path.exists():
            with open(markdown_path, "r") as md_file:
                md_text = md_file.read()
        else:
            md_text = pymupdf4llm.to_markdown(paper)
            markdown_path.write_bytes(md_text.encode("utf-8"))

        # Extract authors
        authors = extract_authors(md_text, args.languages)
        if not authors:
            print(f"Could not identify authors for {paper.stem}")
            continue

        # Count self-citations
        citedmemaybe_report[paper.stem] = count_self_citations(md_text, authors)

    # Write results to CSV
    write_results(citedmemaybe_report)


if __name__ == "__main__":
    args = parse_args()
    main(args)
