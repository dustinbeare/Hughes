# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 14:55:28 2019
Edited on Mon Feb 25 2019 - Dustin Beare - Kentik
@author: mnechikh
"""

import os
import re
import sys
import csv
import json
import time
import logging
import requests
import argparse
from kentikapi.v5 import tagging

logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(levelname)s,%(message)s', stream=sys.stdout)
logger = logging.getLogger()

#===============================================================================

def parse_args():
    # create the main top-level parser
    top_parser = argparse.ArgumentParser()
    subparsers = top_parser.add_subparsers()

    # Optional arguments to control tracing
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--quiet', action='store_true',
        help='Show only minimal output.')
    common.add_argument("--tracelevel", choices=('error', 'warn', 'info', 'debug'), default='info',
        help='Python trace logging level. Default: info')
    common.add_argument('--maxops', type=int, default=None,
        help='Maximum number of REST operations to perform in one run.')
    common.add_argument('--include', type=str, default=None,
        help='Regex that filters which rows are processed. Any value in any field will be matched.')
    common.add_argument('--startrow', type=int, default=None,
        help='The data row in the CSV to start process from. The first data row after the header is row 2.')

    ###############################################################
    # delete-all-populators
    ###############################################################
    p = subparsers.add_parser('delete-all-populators', parents=[common],
        help='Deletes all populators for a given custom dimension')
    p.add_argument('--name', type=str, required=True,
        help='The name of the custom dimension from where all populators will be deleted.')
    p.set_defaults(func=delete_all_populators)

    ###############################################################
    # create-populators
    ###############################################################
    p = subparsers.add_parser('create-populators', parents=[common],
        help='Creates populators for a given existing custom dimension.')
    p.add_argument('--name', type=str, required=True,
        help='The name of the custom dimension under which to create the populators.')
    p.add_argument('--csv', type=str, required=True,
        help='The full path to the CSV file containing the data required to create populators.')
    p.add_argument('--batch', action='store_true',
        help='Create populators using batch mode.')
    p.set_defaults(func=create_populators)

    ###############################################################
    # validate-data
    ###############################################################
    p = subparsers.add_parser('validate-data', parents=[common],
        help='Validates the input data for building populators.')
    p.add_argument('--csv', type=str, required=True,
        help='The full path to the CSV file containing the data required to create populators.')
    p.set_defaults(func=validate)

    if len(sys.argv) == 1:
        top_parser.print_help(sys.stderr)
        sys.exit(1)
    return top_parser.parse_args()

#===============================================================================

def confirm_yes_no(prompt, description=None):

    def print_banner_prompt(prompt, trim=False):
        if trim:
            prompt = ''.join([line.strip(' ') for line in prompt.splitlines(True)])
        max_len = max([len(line) for line in prompt.splitlines()])
        print('#' * max_len)
        print(prompt)
        print('#' * max_len)

    if description:
        print_banner_prompt(description)

    response = input('%(prompt)s (yes/no)[no]: ' % locals())
    result = response.lower() == 'yes'
    return result

def get_auth_headers():
    try:
        return {
            'X-CH-Auth-Email': os.environ['KENTIK_API_USER'],
            'X-CH-Auth-API-Token': os.environ['KENTIK_API_TOKEN']
            }
    except:
        logger.error('You must export the Kentik API key and user via KENTIK_API_TOKEN and KENTIK_API_USER')
        print(
            'These two environment variables must be set before running this script. They are the \n'
            'user name of the person who has admin privileges in Kentik. That person can log in and \n'
            'go to their user profile page and there find the value for the API token.'
            )
        raise Exception('Missing API user or token')

def validate(args):
    '''
    Validate the data we are going to process. Verify that no two CIDR filter strings
    end up being the same for any two devices and that the location IDs created for each
    device are globally unique for all devices in this file
    '''
    location_ids = {}
    cidr_filters = {}
    invalid_rows = []
    with open(args.csv) as instream:
        reader = csv.DictReader(instream, delimiter=',')
        for row in reader:
            location_id = make_location_id(row)
            '''
            Use a set to eliminate differences only in the order of fields.
            For example, (a,b) and (b,a) and techincally duplicates but, compared
            as strings they will equate to different
            '''
            cidr_filter = frozenset(make_cidr_filter(row).split(','))
            if location_id not in location_ids:
                location_ids[location_id] = True
            else:
                invalid_rows.append(reader.line_num)
                logger.error('Duplicate location ID in row %s, %s, %s', reader.line_num, location_id, cidr_filter)
            if cidr_filter not in cidr_filters:
                cidr_filters[cidr_filter] = True
            else:
                invalid_rows.append(reader.line_num)
                logger.error('Duplicate CIDR filter in row %s, %s', reader.line_num, location_id, cidr_filter)
    return invalid_rows

def make_location_id(row):
    location_id = f'{row["HNS_COMPANY_ID"]}-{row["CUSTOMER_LOCATION_ID"]}'
    # Cannot have space in a location ID
    location_id = location_id.replace(' ', '_')
    return location_id

def make_device(row):
    device_regex = f'{row["device_name"]}'
    return device_regex

def netmask_to_cidr(netmask):
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])

def make_cidr(ip_addr, subnet_mask):
    '''
    Given an IP address and mask, turn it into a valid CIDR notation.
    NOTE: This only is designed to handle class-C range subnets
    '''
    assert([int(n) for n in subnet_mask.split('.')][:3] == [255, 255, 255])
    cidr_mask = netmask_to_cidr(subnet_mask)
    return f'{ip_addr}/{cidr_mask}'

def make_cidr_filter(row):
    '''
    Build up a CSV string of CIDR-formatted networks to configured into the populator.
    '''
    cidr_list = []
    for key, value in sorted(row.items()):
        if 'LANIP' in key:
            try:
                if value:
                    lan_id = re.match(r'LANIP(\d+)', key).group(1)
                    addr = value
                    mask = row[f'LANSUBNET{lan_id}']
                    cidr_list.append(make_cidr(addr, mask))
            except Exception as e:
                logger.error('Failed to find find values to create populator for %s, %s, %s', key, row, e)
    return ','.join(cidr_list)

def make_populator_record(row):
    '''
    Build a location string by combining the company ID and location ID to form
    and human-friendly string that will show up in Kentik data tables
    '''
    location_id = f'{row["HNS_COMPANY_ID"]}-{row["CUSTOMER_LOCATION_ID"]}'
    # There has to be at least one CIDR to create a valid populator
    device_id = make_device(row)
    cidr_filter = make_cidr_filter(row)
    if cidr_filter:
        return dict(populator=dict(
            value=location_id,
            addr=cidr_filter,
            device_name=device_id,
            direction='either'))
    else:
        logger.error('Zero LANIP fields found. Cannot create an empty populator')

def get_custom_dimension(dimension_name):
    '''
    Load the custom dimension that matches the provided name and return it to caller
    '''
    url = f'https://api.kentik.com/api/v5/customdimensions'
    response = requests.get(url, headers=get_auth_headers(), timeout=10)
    data = response.json()
    dimension = [d for d in data['customDimensions'] if d['name'] == dimension_name]
    if not dimension:
        raise Exception(f'There is no existing custom dimension named "{dimension_name}"')
    if len(dimension) != 1:
        raise Exception(f'Expected to find only one custom dimension named "{dimension_name}"')
    return dimension[0]

def delete_all_populators(args):
    '''
    Delete all populators that exist under the named custom dimension
    '''
    dimension = get_custom_dimension(args.name)
    populators = dimension['populators']
    if confirm_yes_no(
        f'Are you sure you want to delete {len(populators)} populators for custom dimension "{args.name}"'):
        for n, populator in enumerate(populators, 1):
            url = f'https://api.kentik.com/api/v5/customdimension/{dimension["id"]}/populator/{populator["id"]}'
            response = requests.delete(url, headers=get_auth_headers(), timeout=10)
            logger.info('Deleted [%s]: %s, %s, %s', n, url, response.status_code, response.text)

def create_populator(row, dimension_id, status_callback):
    '''
    Call the Kentik REST API to create the provided populator under the custom
    dimension identified by the provided ID
    '''
    populator = make_populator_record(row)
    if populator:
        url = f'https://api.kentik.com/api/v5/customdimension/{dimension_id}/populator/'
        response = requests.post(url, json=populator, headers=get_auth_headers(), timeout=10)
        if response.status_code == 201:
            status_callback(url, response.status_code, response.text)
        else:
            logger.error('%s, %s', response.text, json.dumps(populator))

def send_batch(batch, args):
    auth = get_auth_headers()
    client = tagging.Client(auth['X-CH-Auth-Email'], auth['X-CH-Auth-API-Token'])
    logger.info('Submitting batch')
    guid = client.submit_populator_batch(args.name, batch)
    # wait up to 60 seconds for the batch to finish:
    for _ in range(1, 12):
        time.sleep(1)
        status = client.fetch_batch_status(guid)
        logger.info('Checking batch progress, Finish = %s', status.is_finished())
        if status.is_finished():
            print("is_finished: %s" % str(status.is_finished()))
            print("upsert_error_count: %s" % str(status.invalid_upsert_count()))
            print("delete_error_count: %s" % str(status.invalid_delete_count()))
            print()
            print(status.pretty_response())
            break

def create_populators(args, batch=None):
    '''
    The input data for this program is expected to be a CSV in the folowing format:

    HNS_COMPANY_ID,CUSTOMER_LOCATION_ID,LANIP1,LANSUBNET1,LANIP2,LANSUBNET2
    SWC,1002,10.50.0.66,255.255.255.192,10.50.0.65,255.255.255.192

    The LANIP2,LANSUBNET2 fields are not actually required. However, this function does
    support N>=1 LANIP/LANSUBNET pairs which are configured as a single, CSV-delimited
    filter in the populator. So, if there are more than one pair, then will all be
    configured but at least one pair must exist as well as all the other fields which
    are also required.
    '''
    row_num = 0
    ops = 0

    def status_callback(*args):
        logger.info('Row %s, %s', row_num, ', '.join([str(n) for n in args]))

    invalid_rows = validate(args)
    with open(args.csv) as instream:
        if args.batch:
            batch = tagging.Batch(replace_all=True)
        else:
            # Cache the dimension id to avoid repeated REST API calls in this loop
            dimension_id = get_custom_dimension(args.name)['id']
        reader = csv.DictReader(instream, delimiter=',')
        for row in reader:
            row_num = reader.line_num
            if row_num in invalid_rows:
                logger.warn('Skipping invalid data in row %s', row_num)
                continue
            if args.startrow and row_num < args.startrow:
                continue
            '''
            If there is an include regex and any value matches it, then we will
            process this record, otherwise, skip this record
            '''
            if args.include and not re.search(args.include, ','.join(row.values())):
                logger.warn('Skipping row %s based on include regex, %s', row_num, row)
                continue
            if not args.batch:
                create_populator(row, dimension_id, status_callback)
            else:
                criteria = tagging.Criteria('either')
                for cidr in make_cidr_filter(row).split(','):
                    criteria.add_ip_address(cidr)
                device_name = make_device(row)
                criteria.add_device_name(device_name)
                location_id = make_location_id(row)
                batch.add_upsert(location_id, criteria)
            ops += 1
            if args.maxops and ops >= args.maxops:
                break
    if args.batch:
        send_batch(batch, args)

def main():
    args = parse_args()
    logging.getLogger().setLevel(args.tracelevel.upper())
    args.func(args)

###########################################################
# MAIN
###########################################################

if __name__ == '__main__':
    main()