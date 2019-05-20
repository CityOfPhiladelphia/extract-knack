import logging
import sys

from extract_knack.cli import extract_records


def handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)

    logger.info('Received event: ' + str(event))

    command = event
    command_name = event['command_name']

    if command_name == 'extract-records':
        extract_records(
            knack_app_id=command['knack_app_id'],
            knack_app_key=command['knack_app_key'],
            object_id=command['object_id'],
            s3_bucket=command['s3_bucket'],
            s3_key=command['s3_key']
        )

    logger.info('Process completed!')