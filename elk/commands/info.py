import os
import re
import configparser

import click
import yaml
from lxml import etree

from elk import config
from elk.logger import Logger
from elk.utils import list_files, Metadata


__all__ = ['info_restore']


INFO_TXT_RE = re.compile(r'''^
    (?P<title>[^\n\r]+)[\n\r]+
    (\((?P<locations>[^\n\r]+)\)[\n\r]+)?
    [\n\r]+
    (?P<description>.+)
$''', re.VERBOSE)


def info_restore(directory):
    logger = Logger('info:restore')

    info_basename = config['info_basename']
    info_filename = os.path.join(directory, info_basename)

    try:
        with open(info_filename, encoding='utf8') as f:
            info = yaml.load(f) or {}
    except FileNotFoundError:
        info = {}

    for filename in list_files(directory):
        restoration_function = select_restoration_function(logger, filename)
        if restoration_function:
            restored_info = restoration_function(logger, filename)
            if restored_info:
                merge_info(info, restored_info)

    with open(info_filename, 'w', encoding='utf8') as f:
        yaml.dump(info, f, **config['yaml'])


def select_restoration_function(logger, filename):
    log_message_prefix = 'Restoring album info from: '

    if os.path.basename(filename) == 'info.txt':
        logger.log(log_message_prefix + click.style('info.txt', bold=True))
        return restore_from_info_txt
    if os.path.basename(filename).lower() == 'feed.rss':
        logger.log(log_message_prefix + click.style('feed.rss', bold=True))
        return restore_from_feed_rss
    if os.path.basename(filename).lower() == 'picasa.ini':
        logger.log(log_message_prefix + click.style('Picasa.ini', bold=True))
        return restore_from_picasa_ini


def merge_info(base_info, info):
    for key, value in info.items():
        if value:
            base_info.setdefault(key, value)


def restore_from_info_txt(logger, filename):
    with open(filename, encoding='utf8') as f:
        text = f.read()
    match = re.search(INFO_TXT_RE, text)

    info = {}
    if match.group('title'):
        info['title'] = match.group('title')
    if match.group('locations'):
        info['locations'] = match.group('locations').split(', ')
    if match.group('description'):
        info['description'] = match.group('description')
    return info


def restore_from_feed_rss(logger, filename):
    directory = os.path.dirname(filename)

    with open(filename) as f:
        xml = etree.parse(f)

    info = {
        'title': xpath_first_as_text(xml, '/rss/channel/title'),
        'description': xpath_first_as_text(xml, '/rss/channel/description'),
    }

    value = xpath_first_as_text(xml, '/rss/channel/gphoto:location')
    if value:
        info['locations'] = [value]
    value = xpath_first_as_text(xml, '/rss/channel/georss:where//gml:pos')
    if value:
        lat, lng = value.split(' ')
        info['coords'] = {'lat': float(lat), 'lng': float(lng)}

    logger.log('Looking for photo details')
    for item_xml in xml.xpath('/rss/channel/item'):
        title = xpath_first_as_text(item_xml, 'title')
        if title:
            photo_filename = os.path.join(directory, title)
            photo_caption = xpath_first_as_text(item_xml, 'description')
            save_photo_caption(logger, photo_filename, photo_caption)


def xpath_first_as_text(xml, query):
    results = xml.xpath(query, namespaces={
        'gphoto': 'http://schemas.google.com/photos/2007',
        'gml': 'http://www.opengis.net/gml',
        'georss': 'http://www.georss.org/georss',
    })
    try:
        first_result = results[0]
    except IndexError:
        return None
    else:
        text = first_result.text
        if text:
            return text.strip()
        else:
            return None


def restore_from_picasa_ini(logger, filename):
    directory = os.path.dirname(filename)

    ini = configparser.ConfigParser()
    ini.read(filename)

    info = {
        'title': ini.get('Picasa', 'name', fallback=None),
        'description': ini.get('Picasa', 'description', fallback=None),
    }
    value = ini.get('Picasa', 'location', fallback=None)
    if value:
        info['locations'] = [value]
    value = ini.get('Picasa', 'geotag', fallback=None)
    if value:
        lat, lng = value.split(',')
        info['coords'] = {'lat': float(lat), 'lng': float(lng)}

    # sections can be e.g. ['Picasa', '070303_183512.jpg', 'photoid']
    logger.log('Looking for photo details')
    for section in ini.sections():
        photo_filename = os.path.join(directory, section)
        photo_caption = ini.get(section, 'caption', fallback=None)
        save_photo_caption(logger, photo_filename, photo_caption)

    return info


def save_photo_caption(logger, filename, caption):
    if not os.path.exists(filename) or not caption:
        return
    basename = os.path.basename(filename)

    meta = Metadata(filename)
    existing_caption = meta['Headline']
    if caption == existing_caption:
        logger.log('{}: {} (already there)'.format(
            click.style(basename, bold=True),
            existing_caption,
        ))
    elif existing_caption:
        logger.log('{}: {} ? {} (keeping original)'.format(
            click.style(basename, bold=True),
            click.style(existing_caption, fg='blue'),
            click.style(caption, fg='blue'),
        ))
    else:
        meta['Headline'] = caption
        logger.log('{}:  -  → {}'.format(
            click.style(basename, bold=True),
            click.style(caption, fg='green'),
        ))
