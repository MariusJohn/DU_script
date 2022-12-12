import urllib
import logging 
import argparse
import csv
from typing import List, NamedTuple
from pathlib import Path
from collections import namedtuple
from encord import EncordUserClient
from encord.project import LabelRowMetadata, EncordClientProject

BENCHMARK_RESULT_FIELDNAMES = [
    'annotatorEmail',
    'filename',
    'classificationName',
    'classificationAnswerName',
    'editorLink',
]
# TODO: replace 'PRIVATE_KEY_FILE_HERE' with the name of the private key file

URLComponents = namedtuple(
    typename='URLComponents',
    field_names=['scheme', 'netloc', 'path', 'url', 'query', 'fragment']
)

SCHEME = "https"
NETLOC = "app.encord.com"
LABEL_EDITOR_PATH_TEMPLATE = "label_editor/{data_hash}&{project_hash}"


def construct_editor_url(project_hash, data_hash):
    url = urllib.parse.urlunparse(URLComponents(
        scheme=SCHEME,
        netloc=NETLOC,
        path=LABEL_EDITOR_PATH_TEMPLATE.format(project_hash=project_hash, data_hash=data_hash),
        url="",
        query="",
        fragment="",
    ))
    return url



def get_encord_project(project_hash: str):
    private_key_path = Path.home() / "ssh_keygen" / "ssh_keygen" 
    
    logging.info(f"reading private key from {private_key_path}")
    with open(private_key_path, 'r') as key_file:
        private_key = key_file.read()

    user_client: EncordUserClient = EncordUserClient.create_with_ssh_private_key(private_key)

    logging.info(f"creating encord project client for {project_hash}")
    project = user_client.get_project(project_hash)

    return project


def fetch_label_rows(project: EncordClientProject, chunk_size: int = 1): 
    metadata: List[LabelRowMetadata] = project.list_label_rows()
    logging.info(f"found {len(metadata)} rows of data")

    for idx in range(0, len(metadata), chunk_size):
        chunk_metadata = metadata[idx:idx+chunk_size]
        chunk_hashs = [i.label_hash for i in chunk_metadata]

        data = project.get_label_rows(chunk_hashs, get_signed_url=False)

        yield from data


if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=str, default='0565412a-d006-4d88-a21b-937576141223')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)

    project = get_encord_project(args.project)

    output_name = '{}_labels.csv'.format(project.title.replace(' ', '_').replace('/','_'))
    
    with open(output_name, 'w', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=BENCHMARK_RESULT_FIELDNAMES)
        writer.writeheader()

        for label_row in fetch_label_rows(project):
            # pick a data_unit to get the anotator
            data_unit = list(label_row['data_units'].values())[0]

            if len(data_unit['labels']['classifications']) == 0:
                continue

            logging.info(f"writing row")

            writer.writerow({
                'annotatorEmail': data_unit['labels']['classifications'][0]['createdBy'],
                'filename': label_row['data_title'],
                'classificationName': list(label_row['classification_answers'].values())[0]['classifications'][0]['name'],
                'classificationAnswerName': list(label_row['classification_answers'].values())[0]['classifications'][0]['answers'][0]['name'],
                'editorLink': construct_editor_url(project,label_row.data_hash)
            })
