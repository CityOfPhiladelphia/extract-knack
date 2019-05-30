from datetime import datetime
import json
import csv
import sys
import os

import click
import requests
import stringcase
import boto3


def get_type(knack_type):
    if knack_type == 'boolean':
        return 'boolean'
    if knack_type == 'number':
        return 'number'
    if knack_type == 'auto_increment':
        return 'integer'
    if knack_type == 'date_time':
        return 'datetime'
    if knack_type == 'multiple_choice':
        return 'array'
    if knack_type == 'address':
        return 'object'
    if knack_type == 'connection':
        return 'array'
    return 'string'

def convert_knack_schema(knack_fields):
    fields = [{
        'name': 'id',
        'type': 'string',
        'constraints': {
            'required': True
        }
    }]

    for field in knack_fields:
        name = (
            stringcase
            .snakecase(field['label'])
            .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .replace('__', '_')
            .replace('_i_d', '_id')
        )

        field_def = {
            'name': name,
            'knack_key': field['key'],
            'knack_type': field['type'],
            'type': get_type(field['type'])
        }

        if field['required'] == True:
            field_def['constraints'] = { 'required': True }

        fields.append(field_def)

    return {
        'primaryKey': ['id'],
        'missingValues': [''],
        'fields': fields
    }

def get_schema(knack_app_id, knack_app_key, object_id):
    response = requests.get(
        'https://api.knack.com/v1/objects/object_{}/fields'.format(object_id),
        headers={
            'X-Knack-Application-Id': knack_app_id,
            'X-Knack-REST-API-KEY': knack_app_key
        })

    data = response.json()

    return convert_knack_schema(data['fields'])

def get_records(knack_app_id, knack_app_key, object_id, page=1, rows_per_page=1000):
    response = requests.get(
        'https://api.knack.com/v1/objects/object_{}/records'.format(object_id),
        params={
            'rows_per_page': rows_per_page,
            'page': page
        },
        headers={
            'X-Knack-Application-Id': knack_app_id,
            'X-Knack-REST-API-KEY': knack_app_key
        })

    data = response.json()

    yield data['records']

    if int(data['current_page']) < data['total_pages']:
        yield from get_records(knack_app_id, knack_app_key, object_id, page=int(data['current_page']) + 1)

def convert_type(local_type, knack_type, value):
    if value == None or value == '':
        return None
    if knack_type == 'connection':
        return json.dumps(list(map(lambda x: x['id'], value)))
    if knack_type == 'phone':
        return value['full']
    if knack_type == 'date_time':
        return datetime.strptime(value['timestamp'], '%m/%d/%Y %I:%M %p').isoformat() + 'Z'
    if local_type == 'array':
        if not isinstance(value, list):
            return json.dumps([value])
        return json.dumps(value)
    if local_type == 'object':
        return json.dumps(value)
    return value

def convert_to_csv_row(schema, record):
    out = {}

    for field in schema['fields']:
        if 'knack_key' in field and (field['knack_key'] + '_raw') in record:
            value = record[field['knack_key'] + '_raw']
        elif 'knack_key' in field and field['knack_key'] in record:
            value = record[field['knack_key']]
        else:
            value = record[field['name']]

        if 'knack_type' in field:
            out[field['name']] = convert_type(field['type'], field['knack_type'], value)
        else:
            out[field['name']] = value

    return out

def load_to_s3(s3_bucket, s3_key, file_path):
    s3 = boto3.resource('s3')
    s3.Object(s3_bucket, s3_key).put(Body=open(file_path, 'rb'))

def clean_up(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

@click.group()
def main():
    pass

@main.command('generate-schema')
@click.argument('knack_app_id')
@click.argument('knack_app_key')
@click.argument('object_id')
@click.option('--indent', type=int, default=None)
@click.option('--s3_bucket', default=None)
@click.option('--s3_key', default=None)
def generate_schema(knack_app_id, 
                          knack_app_key, 
                          object_id, 
                          indent,
                          s3_bucket,
                          s3_key):
    schema = get_schema(knack_app_id, knack_app_key, object_id)

    if (s3_bucket and s3_key):
        output_file = 'schema.json'

        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=indent)

        load_to_s3(s3_bucket, s3_key, output_file)
    else:
        json.dump(schema, sys.stdout, indent=indent)
        sys.stdout.flush()

def extract_records_inner(knack_app_id, 
                          knack_app_key, 
                          object_id,
                          s3_bucket,
                          s3_key):
    schema = get_schema(knack_app_id, knack_app_key, object_id)

    headers = []
    for field in schema['fields']:
        headers.append(field['name'])

    if (s3_bucket and s3_key):
        output_file = 'knack_extract.csv'

        # On Linux, save to tmp folder
        if os.name != 'nt':
            output_file = '/tmp/{}'.format(output_file)
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            writer.writeheader()

            for records_batch in get_records(knack_app_id, knack_app_key, object_id):
                for record in records_batch:
                    out_record = convert_to_csv_row(schema, record)
                    writer.writerow(out_record)

        load_to_s3(s3_bucket, s3_key, output_file)
        clean_up(output_file)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=headers)

        writer.writeheader()

        for records_batch in get_records(knack_app_id, knack_app_key, object_id):
            for record in records_batch:
                out_record = convert_to_csv_row(schema, record)
                writer.writerow(out_record)

        sys.stdout.flush()

@main.command('extract-records')
@click.argument('knack_app_id')
@click.argument('knack_app_key')
@click.argument('object_id')
@click.option('--s3_bucket', default=None)
@click.option('--s3_key', default=None)
def extract_records(knack_app_id, 
                    knack_app_key, 
                    object_id,
                    s3_bucket,
                    s3_key):
    extract_records_inner(knack_app_id, 
                          knack_app_key, 
                          object_id, 
                          s3_bucket, 
                          s3_key)

if __name__ == '__main__':
    main()
