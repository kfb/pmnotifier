# pmnotifier

`pmnotifier` is a small script for OS X that allows you to track changes in Parcel
Monkey's tracking system. It uses basic web scraping to punt changes over to OS X's
Notification Centre.

## Installation

    pip install -r requirements.txt

## Usage

    python pmnotifier.py <invoice number> <shipment id>

Both your invoice number and shipment ID can be found on the Parcel Monkey dashboard.
You don't need the "PM" part of the shipment ID, but `pmnotifier` will strip it out
if it finds one.

When the script first runs, it will create a cache file for your shipment in
`~/.pmnotifier/cachefiles`. The next time it runs (and every subsuquent time), it will
check the current contents of the tracking URL with the cache file, and if any changes
are detected it will flash a notification via Notification Centre.

Works best by adding it to your `crontab`.
