import logging
import sys

from extract_knack.cli import extract_records_inner


def handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)

    logger.info('Received event: ' + str(event))

    command = event
    command_name = event['command_name']

    if command_name == 'extract-records':
        extract_records_inner(
            knack_app_id=command['app-id'],
            knack_app_key=command['app-key'],
            object_id=command['object-id'],
            s3_bucket=command['s3_bucket'],
            s3_key=command['s3_key']
        )

    logger.info('Process completed!')