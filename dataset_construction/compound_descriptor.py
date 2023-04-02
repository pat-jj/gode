import requests
from tqdm import tqdm
from multiprocessing import Pool

import re

def retrive_value(response):
    # assuming the HTML response is stored in the variable 'html'
    has_value_pattern = r'<span class="value">([\d.]+)</span>'
    has_value_match = re.search(has_value_pattern, response)

    if has_value_match:
        value = has_value_match.group(1)
        return value
    else:
        return None

def process_lines(lines):
    triple_set = set()
    for line in lines:
        h, r, t = line.split('\t')
        t = t[:-1]
        t_query = t.replace('descriptor:', '')
        rel = t_query.replace(t_query.split('_')[0]+'_', '')

        # Use a session object to reuse connections
        session = requests.Session()
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/rdf/descriptor/{t_query}.html"

        # Query the API and parse the response
        response = session.get(url).text

        value = retrive_value(response)

        triple = (h, rel, value)
        triple_set.add(triple)

    return triple_set

if __name__ == '__main__':
    with open('./compound_descriptor.txt', 'r') as f:
        lines = f.readlines()

    rel_set = set()
    for line in lines:
        t = line.split('\t')[2][:-1]
        t_query = t.replace('descriptor:', '')
        rel = t_query.replace(t_query.split('_')[0]+'_', '')
        rel_set.add(rel)

    # Split the lines list into sub-lists of size 1000
    batch_size = 1000
    line_batches = [lines[i:i+batch_size] for i in range(0, len(lines), batch_size)]

    with Pool() as pool:
        results = list(tqdm(pool.imap(process_lines, line_batches), total=len(line_batches), desc="Processing batches"))

    # Merge the results into a single set
    triple_set = set()
    for result in results:
        triple_set.update(result)

    # do something with triple_set, e.g. write to file
    out_str = ""
    for triple in triple_set:
        h, r, t = triple
        out_str += h + '\t' + r + '\t' + t +'\n'

    with open('./compound_descriptor_triple.txt', 'w') as f:
        f.write(out_str)
