from datetime import datetime
import json
import csv
import sys

import click
import requests
import stringcase

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

@click.group()
def main():
    pass

@main.command('generate-schema')
@click.argument('knack_app_id')
@click.argument('knack_app_key')
@click.argument('object_id')
@click.option('--indent', type=int, default=None)
def generate_schema(knack_app_id, knack_app_key, object_id, indent):
    schema = get_schema(knack_app_id, knack_app_key, object_id)

    click.echo(json.dumps(schema, indent=indent))

@main.command('extract-records')
@click.argument('knack_app_id')
@click.argument('knack_app_key')
@click.argument('object_id')
def extract_records(knack_app_id, knack_app_key, object_id):
    schema = get_schema(knack_app_id, knack_app_key, object_id)

    headers = []
    for field in schema['fields']:
        headers.append(field['name'])

    writer = csv.DictWriter(sys.stdout, fieldnames=headers)

    writer.writeheader()

    for records_batch in get_records(knack_app_id, knack_app_key, object_id):
        for record in records_batch:
            out_record = convert_to_csv_row(schema, record)
            writer.writerow(out_record)

if __name__ == '__main__':
    main()
