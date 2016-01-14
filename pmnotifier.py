#!/usr/bin/env python
#
# An OS X utility to show notifications when the tracking status of a Parcel Monkey
# consignment changes.
#
# Designed to be run via cron.
#
# Usage: pmnotifier.py <invoice number> <shipment id>

import os
import sys
import requests

from lxml import html

# Configuration. You probably don't need to edit this.
CACHE_PATH = '{}/.pmnotifier/cachefiles'.format(os.getenv('HOME'))
PM_TRACKING_URL = 'https://www.parcelmonkey.co.uk/tracking.php?PMID=PM_{}_{}'


def entry_content(element):
    content = ''

    # Does the element contain a '<strong>' portion?
    if element.xpath('strong') is not None:
        content += '{}: '.format(element.xpath('strong/text()')[0].replace(':', ''))

    for text in element.xpath('text()'):
        content += '{} '.format(text.strip())

    return content


def page_changes(old_content, new_content):
    # Find the <ul> in the page (there should only be one)
    old_tree = html.fromstring(old_content)
    new_tree = html.fromstring(new_content)

    xpath_expression = '//ul[@class="list--striped push-bottom"]/li'

    old = [entry_content(e) for e in old_tree.xpath(xpath_expression)]
    new = [entry_content(e) for e in new_tree.xpath(xpath_expression)]

    return [e for e in new if e not in old]


def notify(message, tracking_id):
    os.system('osascript -e \'display notification "{}" with title "{}"\''.format(
        message,
        'Package Monkey Update ({})'.format(tracking_id),
    ))


if __name__ == '__main__':
    # Parse the command line arguments.
    invoice_num = sys.argv[1].upper()
    shipment_id = sys.argv[2].upper()

    # Strip the 'PM' prefix if present
    shipment_id = shipment_id.replace('PM', '')

    cachefile = os.path.join(CACHE_PATH, '{}_{}'.format(invoice_num, shipment_id))
    tracking_url = PM_TRACKING_URL.format(invoice_num, shipment_id)

    # Create the cache path if it doesn't exist
    if not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    # Try to open the cached page. If it doesn't exist, create it and exit.
    if not os.path.isfile(cachefile):
        with open(cachefile, 'w') as f:
            f.write(requests.get(tracking_url).content)

        sys.exit(0)

    # The file already exists, so pull down a new copy and see if they've changed
    old_content = open(cachefile, 'r').read()
    new_content = requests.get(tracking_url).content

    # If the content has changed, parse the pages to get the differences
    # if old_content != new_content:
    for change in page_changes(old_content, new_content):
        notify(change, '{}_{}'.format(invoice_num, shipment_id))

    # Save the cache file
    with open(cachefile, 'w') as f:
        f.write(new_content)
