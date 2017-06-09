# -*- coding: utf-8 -*-
'''
ニコニコから画像をダウンロードしてくるスクリプト
'''

from urllib.request import build_opener, HTTPCookieProcessor, ProxyHandler
from urllib.parse import urlencode
from http.cookiejar import CookieJar
import pprint
import json
from bs4 import BeautifulSoup
import os
import argparse

# ニコニコの認証処理をするメソッド
def authenticate(mail_add, passwd):
    proxy = ProxyHandler({'http': 'http://proxy.nagaokaut.ac.jp:8080',
                          'https': 'http://proxy.nagaokaut.ac.jp:8080'})
    post = {
        'mail_tel': mail_add,
        'password': passwd
    }

    data = urlencode(post).encode('utf-8')
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj), proxy)
    res = opener.open('https://secure.nicovideo.jp/secure/login', data)

    if not 'user_session' in cj._cookies['.nicovideo.jp']['/']:
                raise Exception('PermissionError')

    else:
        return opener

# クエリから画像のIDを検索
def search(query, get_num, opener):
    url = 'http://api.search.nicovideo.jp/api/v2/illust/contents/search?'
    offset = 0
    payload = {
        'q': query,
        'targets': 'tags',
        'fields': 'contentId',
        '_sort': 'viewCounter',
        '_limit': get_num,
        '_offset': offset}

    data = urlencode(payload)
    res = opener.open(url+data)
    search_data = json.loads(res.read().decode('utf-8'))

    img_url_list = []
    for id in search_data['data']:
        img_url = 'http://seiga.nicovideo.jp/image/source?id={}'.format(id['contentId'][2:])
        img_url_list.append(img_url)

    return img_url_list

# 画像のダウンロード
def get_img(img_url_list, opener, output_path):
    cnt = 0
    result = []
    for i in img_url_list:
        raw_url = opener.open(i)
        soup = BeautifulSoup(raw_url.read().decode('utf-8'), 'html.parser')
        source_url = soup.find(class_='illust_view_big').find('img')['src']
        img_res = opener.open('http://lohas.nicoseiga.jp' + source_url)

        filename = output_path + '/{}.jpg'.format(cnt)
        with open(filename, 'wb') as f:
            f.write(img_res.read())

        cnt += 1

def main():
    parser = argparse.ArgumentParser(
        description='download image from flicker')
    parser.add_argument('query', help='search word')
    parser.add_argument('num', help='file number max = 500')
    parser.add_argument('--output', '-o', default="./", help='save dir')
    args = parser.parse_args()
    mail_add = ''
    passwd = ''
    query = args.query
    num = args.num

    output_path = os.path.realpath(args.output + query)
    if os.path.exists(output_path) is False:
        os.mkdir(output_path)

    opener = authenticate(mail_add, passwd)
    img_url_list = search(query, num, opener)

    get_img(img_url_list, opener, output_path)

if __name__ == '__main__':
    main()
