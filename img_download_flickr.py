# -*- coding: utf-8 -*-

import requests
import argparse
import os


def main():
    """Download image  use flicker api."""
    parser = argparse.ArgumentParser(
        description='download image from flicker')
    parser.add_argument('query', help='search word')
    parser.add_argument('num', help='file number max = 500')
    parser.add_argument('--output', '-o', default="./", help='save dir')

    args = parser.parse_args()

    url = 'https://api.flickr.com/services/rest/'
    api_key = 'your api key'
    query = args.query
    page_num = args.num

    if int(page_num) > 500:
        page_num = 500

    output_path = os.path.realpath(args.output + query)
    if os.path.exists(output_path) is False:
        os.mkdir(output_path)

    payload = {
        'method': 'flickr.photos.search',
        'api_key': api_key,
        'text': query,
        'per_page': page_num,
        'format': 'json',
        'nojsoncallback': '1'}

    proxy = {'http': 'http://proxy.example.co.jp:xxxx',
             'https': 'http://proxy.example.co.jp:xxxx'}
    r = requests.get(url, params=payload, proxies=proxy)

    search_data = r.json()

    url_param = [(i['farm'], i['server'], i['id'], i['secret'])
                 for i in search_data['photos']['photo']]

    cnt = 0
    for parms in url_param:
        img_url = 'https://farm{}.staticflickr.com/{}/{}_{}.jpg'.format(
            parms[0], parms[1], parms[2], parms[3])

        r = requests.get(img_url, proxies=proxy)

        filename = output_path + '/{}.jpg'.format(cnt)
        with open(filename, 'wb') as f:
            f.write(r.content)

        cnt += 1


if __name__ == '__main__':
    main()
