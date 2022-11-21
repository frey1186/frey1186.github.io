#!/usr/bin/env python3
#
#  file name :  search_readpaper.py
#  useage    :  python3 search_redpaper.py  SEARCH_STRING
#               python3 search_redpaper.py  SEARCH_STRING -d Index
#  date      :  2019.09.19
#

import requests
import bs4
import re
import sys
import os


help_txt='''
find a Paper : search_redpaper.py  SEARCH_STRING
find and download with index id:  search_redpaper.py  SEARCH_STRING -d Index
'''
try:
    search_str = sys.argv[1]
    url = 'http://www.redbooks.ibm.com/redbooks.nsf/searchsite?SearchView=&query=%s&SearchWV=true' % search_str
    html_txt = requests.get(url=url).text
    sp = bs4.BeautifulSoup(html_txt, 'html.parser')

    search_ret_list = sp.select('#tab1')[0]
    # print(sp.find('p', class_=re.compile(r'ibm-padding-bottom.*')))
    # print(search_ret_list)

    ret_title_list = search_ret_list.select('a')
    ret_desc_list = search_ret_list.select('.ibm-padding-bottom-1')
except:
    print(help_txt)
    exit(0)

if len(sys.argv) == 4 :
    if sys.argv[2] == '-d':
        try:
            download_index = int(sys.argv[3])
            title_rename = ret_title_list[download_index-1].text.replace(' ','-')
            paper_id_href = ret_title_list[download_index-1].attrs['href']
            paper_id_real = re.findall('redp[0-9]+|sg[0-9]+', paper_id_href)[0]
            if 'redp' in paper_id_real:
                print("Downloading the %s.pdf ..." % paper_id_real)
                os.system('wget "https://www.redbooks.ibm.com/redpapers/pdfs/%s.pdf" -O "%s-%s".pdf'
                          % (paper_id_real, paper_id_real, title_rename))
                os.system('wget "https://www.redbooks.ibm.com/redpieces/pdfs/%s.pdf" -O "%s-%s".pdf'
                          % (paper_id_real, paper_id_real, title_rename))
            elif 'sg' in paper_id_real:
                print("Downloading the %s.pdf" % paper_id_real)
                os.system('wget "https://www.redbooks.ibm.com/redbooks/pdfs/%s.pdf" -O "%s-%s".pdf'
                          % (paper_id_real, paper_id_real, title_rename))
            else:
                print("Not Download.... ")
        except:
            print("Wrong input!! May be can not find the Paper ID... Plese try again...")
    else:
        print("Wrong input!!  Try again...")
        print(help_txt)
elif len(sys.argv) == 2:
    for i in range(len(ret_title_list)):
        title = ret_title_list[i].text
        paper_id = ret_title_list[i].attrs['href']
        # desc = ''
        desc = ret_desc_list[i].text
        print('''
[%s] [%s] %s
%s
''' % (i+1, paper_id, title, desc))
else:
    print("Wrong input!!  Try again...")




