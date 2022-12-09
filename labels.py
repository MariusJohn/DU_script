import csv
from typing import List
import os
from pathlib import Path

from encord import EncordUserClient
from encord.project import LabelRow, LabelRowMetadata

BENCHMARK_RESULT_FIELDNAMES = [
    'annotatorEmail',
    'filename',
    'classificationName',
    'classificationAnswerName',
]

# TODO: replace 'PRIVATE_KEY_FILE_HERE' with the name of the private key file
private_key_path = os.path.join(Path.home(), "./ssh",  "PRIVATE_KEY_FILE_HERE")

with open(private_key_path, 'r') as key_file:
    private_key = key_file.read()

if '__main__' == __name__:
    user_client: EncordUserClient = EncordUserClient.create_with_ssh_private_key(private_key)

    # project_hash = 'db1769bc-1b6d-4802-a667-417b45295af4'
    project_hash = '893b3432-a513-4064-93dd-8bd7fc5efbab'
    project = user_client.get_project(project_hash)

    output_name = '{}_labels.csv'.format(project.title.replace(' ', '_').replace('/','_'))
    output_file = open(output_name, 'w', encoding='utf-8')
    
    writer = csv.DictWriter(output_file, fieldnames=BENCHMARK_RESULT_FIELDNAMES)
    writer.writeheader()

    # we want one csv for entire project
    label_row_metadata: List[LabelRowMetadata] = project.list_label_rows()
    all_label_rows: List[LabelRow] = project.get_label_rows(
        [lrmd.label_hash for lrmd in label_row_metadata],
        get_signed_url=False
    )

    for label_row in all_label_rows:
        # pick a data_unit to get the anotator
        data_unit = list(label_row['data_units'].values())[0]

        if len(data_unit['labels']['classifications']) == 0:
            continue

        writer.writerow({
            'annotatorEmail': data_unit['labels']['classifications'][0]['createdBy'],
            'filename': label_row['data_title'],
            'classificationName': list(label_row['classification_answers'].values())[0]['classifications'][0]['name'],
            'classificationAnswerName': list(label_row['classification_answers'].values())[0]['classifications'][0]['answers'][0]['name'],
        })
