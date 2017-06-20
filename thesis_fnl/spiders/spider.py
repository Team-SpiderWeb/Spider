import scrapy
from scrapy_splash import SplashRequest
from thesis_fnl.items import ThesisFnlItem
import json
import js2xml
import re
from bs4 import BeautifulSoup

class Spider(scrapy.Spider):

    name = "rappler"

    sitemapurls = []

    with open('sitemap.json') as jsonfile:
        data = json.load(jsonfile)

    for index, element in enumerate(data):  
        url = data[index]['url']
        sitemapurls.append(url)

    start_urls = sitemapurls

    # NORMAL
    # start_urls = ["http://www.rappler.com/rappler-blogs/buena-bernal/82375-pope-francis-coverage-non-catholic-reporter"]
    # start_urls = ["http://www.rappler.com/entertainment/news/124642-maria-ozawa-denies-one-night-stand-cesar-montano"]
    # start_urls = ["http://www.rappler.com/entertainment/news/160152-uncut-fifty-shades-darker-mtrcb-rating"]
    
    # WITH FULLTEXT
    # start_urls = ["http://www.rappler.com/world/regions/asia-pacific/172250-south-korea-freeze-new-thaad-deployment-pending-probe"]
    # start_urls = ["http://www.rappler.com/world/regions/us-canada/172872-trump-south-korea-moon-north-korea-talks"]
    
    # IMAGE ONLY
    # start_urls = ["http://www.rappler.com/pugad-baboy/83203-excuses"]

    allowed_domains = ["www.rappler.com"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 10}
            )


    def parse(self, response):
        for rappler in response.css('div.ob-widget-section.ob-last'):
            rapplerStory = response.css('div.story-area')
            item = ThesisFnlItem()

            title = response.css('title::text').extract_first()

            try:
                js = response.xpath('//script/text()').extract()
                jstree = js2xml.parse(js[1])
                content = js2xml.jsonlike.make_dict(jstree.xpath('//var[@name="r4articleData"]//object//property[@name="fulltext"]')[0])
                cleantext = BeautifulSoup(str(content)).text
                content = re.sub('fulltext', '', cleantext, 1)
                content = re.sub('[^A-Za-z0-9\.]+', ' ', content)
                item["content"] = content
            except:
                try:
                    content = response.xpath('//div[starts-with(@class,"story-area")]//p//text() | //div[starts-with(@class,"story-area")]//p/span//text()').extract()
                    item["content"] = u','.join(content)
                except:
                    item["content"] = ""  

            # item["content"] = response.xpath('//div[starts-with(@class,"story-area")]//p//text() | //div[starts-with(@class,"story-area")]//p/span//text()').extract()
            item["url"]= response.url
            item["title"] = title

            link = rappler.css('a::attr(href)').extract()
            link_par = rapplerStory.css('p>a::attr(href)').extract()
            
            try:
                if link_par[0] is not None:
                    link.append(link_par[0])
                if link_par[1] is not None:
                    link.append(link_par[1])
            except IndexError:
                pass

            item["link"] =  link

            yield item
            
            next_page = link

            countNext = 0

            for i in next_page:
                if next_page[countNext] is not None: 
                    next_page[countNext] = response.urljoin(next_page[countNext])
                    countNext+=1
            
            countNext = 0
            for j in next_page:
                yield SplashRequest(next_page[countNext], self.parse,
                     endpoint='render.html',
                     args={'wait': 10}, dont_filter="TRUE"
                  )
                countNext+=1
               
             
