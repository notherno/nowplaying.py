#!/usr/bin/env python
# coding: utf-8

import sys, json, os.path
from appscript import *
from xml.etree.ElementTree import *
from requests_oauthlib import OAuth1Session
from bottlenose import api
from optparse import OptionParser

################################################################################
# Function definitions
################################################################################

# Search with Amazon product API for 'search_index' includes the 'keywords'
def item_search(keywords, search_index, item_page = 1, resg = 'Small'):
    response = amazon.ItemSearch(
        SearchIndex = search_index,
        Keywords = keywords,
        ItemPage = item_page,
        ResponseGroup = resg
    )

    elem = fromstring(response)
    ns = elem.tag.split('}')[0] + '}'
    dp_asin = elem.find('./{0}Items/{0}Item/{0}ASIN'.format(ns))
    dp_title = elem.find('./{0}Items/{0}Item/{0}ItemAttributes/{0}Title'.format(ns))

    if dp_asin is None:
        item_url = ''
    else:
        item_url = 'http://www.amazon.co.jp/dp/{0}/'.format(dp_asin.text)

    if dp_title is None:
        item_title = ''
    else:
        item_title = dp_title.text

    return (item_title, item_url)


# Twitter authorization and tweet the 'message'
def tweet (message, CK, CS, AT, AS):
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    params = {'status': message}

    # OAuth and HTTP post
    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.post(url, params = params)

    # check response
    return req.status_code


# if the length of 'string' is larger than 'l', excerpt the 'string' and put 'sep'
def excerpt (string, l, sep):
    if len(string) > l:
        return string[:l] + sep
    else:
        return string

def asc (unic, ENCODING):
    return unic.encode(ENCODING)

################################################################################
# Function definitions
################################################################################

if __name__ == '__main__':
    CONFIG_FILE = 'config.json'
    ENCODING = 'utf-8'

    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = current_dir + '/' + CONFIG_FILE

    if not os.path.isfile(config_path):
        exit('ERROR: config.json does not exist')

    source = u''
    for line in [l.strip() for l in open(config_path, 'r').read().decode(ENCODING).split('\n')]:
        if line and line[0] != '/':
            source += line

    CONF = json.loads(source)

    # option parser
    parser = OptionParser(usage = 'usage: %prog [options] message')

    parser.add_option(
        '-q', '--quiet',
        dest = 'tweet',
        action = 'store_false',
        default = True,
        help = 'don\'t tweet and just display information for the song now playing'
    )

    parser.add_option(
        '-r', '--rate',
        dest = 'rating',
        help = 'rate the song now playing'
    )

    parser.add_option(
        '-n', '--no-amazon',
        dest = 'amazon',
        action = 'store_false',
        default = True,
        help = 'don\'t search product in Amazon API'
    )

    (options, args) = parser.parse_args()

    # preparation for amazon API access
    amazon = api.Amazon(
        asc(CONF['amazon']['access_key'], ENCODING),
        asc(CONF['amazon']['secret_key'], ENCODING),
        asc(CONF['amazon']['assoc_tag'], ENCODING),
        Region = CONF['amazon']['region']
    )

    # fetching the song that iTunes is playing
    itunes = app('iTunes')
    track = itunes.current_track

    if options.amazon:
        if len(track.album.get()) < CONF['amazon']['threshold']:
            query = track.artist.get() + ' ' + track.album.get()
        else:
            query = track.album.get()

        (product_title, amazon_url) = item_search(query, CONF['amazon']['search_index'])
        print('[Amazon search result]')
        if not product_title:
            print('No product for ' + query)
        else:
            print(product_title + '\n<' + amazon_url + '>\n')

    else:
        (product_title, amazon_url) = ('', '')

    if options.rating:
        # numbers of rating stars of iTunes is from 0 to 5 (exact value is from 0 to 100)
        if options.rating in [str(i) for i in range(6)]:
           track.rating.set(int(options.rating) * 20)
        else:
            exit('ERROR: Invalid value for RATING')

    stars = int(track.rating.get()) / 20
    rating = CONF['appearance']['symbols']['rated_symbol'] * stars + CONF['appearance']['symbols']['not_rated_symbol'] * (5 - stars) if stars > 0 else u''

    message = CONF['appearance']['tweet_format'].format(
        title = excerpt(
            track.name.get(),
            CONF['appearance']['limits']['title'],
            CONF['appearance']['symbols']['excerpt_symbol']
        ),
        artist = excerpt(
            track.artist.get(),
            CONF['appearance']['limits']['artist'],
            CONF['appearance']['symbols']['excerpt_symbol']
        ),
        album = excerpt(
            track.album.get(),
            CONF['appearance']['limits']['album'],
            CONF['appearance']['symbols']['excerpt_symbol']
        ),
        rating = rating,
        comment = args[0].decode(ENCODING) if len(args) > 0 else u'',
        url = amazon_url,
        product = product_title
    ).encode(ENCODING).strip()

    # show formatted message
    print('=' * CONF['appearance']['horizontal_line'])
    print(message)
    print('=' * CONF['appearance']['horizontal_line'])

    if options.tweet:
        status_code = tweet(
            message,
            asc(CONF['twitter']['consumer_key'], ENCODING),
            asc(CONF['twitter']['consumer_secret'], ENCODING),
            asc(CONF['twitter']['access_token'], ENCODING),
            asc(CONF['twitter']['access_token_secret'], ENCODING)
        )
        if status_code == 200:
            print(CONF['appearance']['tweet_success_message'].format(status_code = status_code))
        else:
            print(CONF['appearance']['tweet_error_message'].format(status_code = status_code))
