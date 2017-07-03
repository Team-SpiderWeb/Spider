import scrapy
from scrapy.conf import settings
import os
import os.path
from scrapy_splash import SplashRequest
from thesis_fnl.items import ThesisFnlItem
import json
import js2xml
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib


class Spider(scrapy.Spider):

    name = "rappler"
    html_ctr = 0
    sitemapurls = []

    with open('/Users/rizab/Desktop/THESIS/Python/sitemap/result.json') as jsonfile:
        data = json.load(jsonfile)
    
    for u in data['sitemap']:
        sitemapurls.append(u['url'])

    start_urls = sitemapurls

    allowed_domains = ["www.rappler.com"]

    def start_requests(self):
        
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 10}
            )


    def parse(self, response):
        valid_url = 'http://www.rappler.com'
        parlink_count = 0
        templinks = []

        for rappler in response.css('div.ob-widget-section.ob-last'):

            rapplerStory = response.css('div.story-area')
            item = ThesisFnlItem()

            title = response.css('title::text').extract_first()

            if not os.path.exists(settings['HTML_OUTPUT_DIRECTORY']):
                os.makedirs(settings['HTML_OUTPUT_DIRECTORY'])

            self.html_ctr += 1
            
            filename = '%s/%d.html' % (settings['HTML_OUTPUT_DIRECTORY'], self.html_ctr)
            with open(filename, 'wb') as f:
               f.write(response.body)

            page = urllib.request.urlopen(response.url).read()
            soup = BeautifulSoup(page, "lxml")

            author = soup.find('meta', attrs={'name':'bt:author'}) 
            date = soup.find('meta', attrs={'name':'bt:pubDate'}) 

            if author:
                item["author"] = author.get('content')
            if date:
                item["date"] = date.get('content')

            try:
                js = response.xpath('//script/text()').extract()
                jstree = js2xml.parse(js[1])
                content = js2xml.jsonlike.make_dict(jstree.xpath('//var[@name="r4articleData"]//object//property[@name="fulltext"]')[0])
                cleantext = BeautifulSoup(str(content), "lxml").text
                content = re.sub('fulltext', '', cleantext, 1)
                content = re.sub('[^A-Za-z0-9\.]+', ' ', content)
                item["content"] = content
            except:
                try:

                    content = response.xpath('//div[starts-with(@class,"story-area")]//p//text()[not(ancestor::script|ancestor::style|ancestor::noscript)] | //div[starts-with(@class,"story-area")]//p/span//text()').extract()
                    item["content"] = u','.join(content)

                except:
                    item["content"] = ""  

            item["url"]= response.url
            item["title"] = title

            link = rappler.css('a::attr(href)').extract()
            par_link = rapplerStory.css('p>a::attr(href)').extract()
           
            for rap_link in par_link:
                if parlink_count < 2:
                    parsed_uri = urlparse(rap_link)
                    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

                    if valid_url in domain and 'indonesia' not in domain:
                        link.append(rap_link)
                        parlink_count+=1

            item["link"] = link

            yield item
            
            next_page = link          
            countNext = 0
            for j in next_page:
                yield SplashRequest(response.urljoin(next_page[countNext]), self.parse,
                     endpoint='render.html',
                     args={'wait': 10}
                  )
                countNext+=1

