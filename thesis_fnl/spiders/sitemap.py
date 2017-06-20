import scrapy
from scrapy.spiders import SitemapSpider
from scrapy.selector import Selector

class SmapSpider(SitemapSpider):
    name="sitemap"
    sitemap_urls = ['http://www.rappler.com/sitemap-2015.xml']
    count=0
    
    def parse(self,response):
        return scrapy.Request(response.url, callback=self.parse_sitemap_url)

    def parse_sitemap_url(self, response):
        while count <= 5:
            self.count=self.count+1

            yield {
            	'url': response.url
            }
        

        # sel=Selector(response)
        # print(str(self.count)+":\t"+response.url)
        # sel.xpath('/html/head/title/text()').extract()