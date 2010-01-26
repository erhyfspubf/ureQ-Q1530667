import urllib

class VkontakteApi(object):
    def __call__(self):
        query = self.request.get('QUERY_STRING')
        return urllib.urlopen("http://api.vkontakte.ru/api.php?" + query).read()
