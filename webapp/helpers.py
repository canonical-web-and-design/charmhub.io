import datetime

from flask import request
import humanize
from dateutil import parser


def split_filters(filters):
    filter_params = {}

    for charm_filter in filters:
        if charm_filter not in filter_params:
            filter_params[charm_filter] = []

        filter_params[charm_filter] += filters[charm_filter].split(",")

    return filter_params


def join_filters(filters):
    filter_string = []

    for filter_type in filters:
        if len(filters[filter_type]) > 0:
            filter_type_filters = ",".join(filters[filter_type])
            filter_string.append(f"{filter_type}={filter_type_filters}")

    if len(filter_string) == 0:
        filter_string = ""
    elif len(filter_string) == 1:
        filter_string = f"?{filter_string[0]}"
    else:
        filter_string = f"?{'&'.join(filter_string)}"

    return filter_string


def add_filter(filter_type, filter_name):
    filters = split_filters(request.args)
    new_filters = filters.copy()
    if filter_type not in new_filters:
        new_filters[filter_type] = [filter_name]
    elif filter_name not in new_filters[filter_type]:
        new_filters[filter_type].append(filter_name)

    return join_filters(new_filters)


def remove_filter(filter_type, filter_name):
    filters = split_filters(request.args)
    new_filters = filters.copy()
    if filter_type in new_filters and filter_name in filters[filter_type]:
        new_filters[filter_type].remove(filter_name)

    return join_filters(new_filters)


def active_filter(filter_type, filter_name):
    filters = split_filters(request.args)
    if filter_type in filters and filter_name in filters[filter_type]:
        return True

    return False


def convert_date(date_to_convert):
    """Convert date to human readable format: Month Day Year
    If date is less than a day return: today or yesterday
    Format of date to convert: 2019-01-12T16:48:41.821037+00:00
    Output: Jan 12 2019
    :param date_to_convert: Date to convert
    :returns: Readable date
    """
    date_parsed = parser.parse(date_to_convert).replace(tzinfo=None)
    delta = datetime.datetime.now() - datetime.timedelta(days=1)
    if delta < date_parsed:
        return humanize.naturalday(date_parsed).title()
    else:
        return date_parsed.strftime("%-d %B %Y")


def is_safe_url(url):
    """
    Return True if the URL is inside the same app
    """
    if url.startswith(request.url_root) or url.startswith("/"):
        return True
    return False
