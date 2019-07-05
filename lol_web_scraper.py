#! "C:\Users\Joni\source\repos\lol_web_scraper\env1\Scripts\python.exe"

import os, sys
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def find_role(html, opp=''):
    for container in html.select('div', {'class' : 'role-filter-container'}):
        role = container.find('div', { 'class' : 'active'})
        if role is not None:
            if len(opp) > 1:
                opp=opp[0].upper() + opp[1:]
                print('Runes for role: ' + role['data-tip'] + ' against ' + opp)
                return
            print('Runes for role: ' + role['data-tip'])
            return

def find_main_runes(html):

    main_tree_found = False
    print('\nMain rune tree:')
    for p in html.select('div', { "class" : "rune-trees-container"}):
        '''
        Get main tree runes
        '''
        if p.get('class') is not None and 'primary-perk' in p.get('class'):
            children = p.findChildren('div', { 'class' : 'perk-active'}, recursive=False)
            if main_tree_found is False and len(children) > 0 and children[0].find() is not None:
                main_image_url = children[0].find('img', recursive=False).get('src')
                main_tree = main_image_url.split('/')[-3]
                print(main_tree+'\n\nRunes:')
                main_tree_found = True
            for child in children:
                # We should get only one child
                image_url = child.find('img', recursive=False).get('src')
                main_rune = image_url.split('/')[-1:][0].split('.')[0]
                print(main_rune)

def find_secondary_runes(html):
    sec_tree_found = False
    print('\nSecondary rune tree:')

    for p in html.select('div', { "class" : "rune-trees-container"}):
        if p.get('class') is not None and 'perks' in p.get('class') and 'primary-perk' not in p.get('class') and p.find() is not None:
            sub_children = p.findChildren('div', { 'class' : 'perk-active'}, recursive=False)
            if sec_tree_found is False and len(sub_children) > 0 and sub_children[0].find() is not None:
                sub_image_url = sub_children[0].find('img', recursive=False).get('src')
                sub_tree = sub_image_url.split('/')[-3]
                print(sub_tree+'\n\nRunes:')
                sec_tree_found = True
            for sub_child in sub_children:
                # We should get only one child
                image_url = sub_child.find('img', recursive=False).get('src')
                main_rune = image_url.split('/')[-1:][0].split('.')[0]
                print(main_rune)

def parse_shard(url):
    img = url.split('/')[-1:][0].split('.')[0]
    print(img[8:-4])

def find_shards(html):
    print('\nShards:')
    p = html.select('div', { "class" : "stat-shards-container"})
    active_shard = p[0].findChildren('div', {"class":"shard-active"})
    for shard in active_shard:
        if shard is not None and len(active_shard) > 0:
            parsed_shard = parse_shard(shard.img['src'])


def find_runes(url, opp):
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    find_role(html, opp)
    find_main_runes(html)
    find_secondary_runes(html)
    find_shards(html)
   
def check_exit(inp):
    '''
    Returns true when user wants to quit
    '''
    if inp == 'exit' or inp == 'q':
        return True
    return False

def check_valid_champ(champ):
    data = {}
    champions = []
    with open('champions.json', 'r') as f:
        data = json.load(f)
    for p in data:
        champions.append(p['id'].lower())
    if champ.lower() in champions:
        return True
    return False

def main_loop():
    quit = False
    while(quit == False):
        champion_or_exit = input('\nChoose champion, type exit to quit\n').lower()
        quit = check_exit(champion_or_exit)
        if quit == True:
            continue
        if not check_valid_champ(champion_or_exit):
            continue
        role = input('Pick role, where you play your champion. (top/jungle/middle/adc/support). Type exit to quit\n')
        quit = check_exit(role)
        if quit == True:
            continue
        roles = ['top', 'jungle', 'middle', 'adc', 'support', '']
        if role not in roles:
            print('Not valid role')
            continue
        opp = input('Pick opponent, who u are playing against in set lane.\n\
Press just enter without input if u want just default runeset. Type exit to quit\n')
        url = 'https://u.gg/lol/champions/'+ champion_or_exit +'/build?role='+role+'&opp='+opp
        find_runes(url, opp)

main_loop()