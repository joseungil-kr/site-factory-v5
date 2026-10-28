import unittest
from html.parser import HTMLParser
from v5.markup import document_directory, related_documents, url_path


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.hrefs=[]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag=='a':
            self.hrefs.append(dict(attrs)['href'])


class PlantDiscoveryTests(unittest.TestCase):
    def test_directory_reaches_every_document_and_preserves_404_alias(self):
        pages=[dict(number=n,region='서울 강남구 역삼동',topic='축하화분') for n in range(1,3466)]
        links=Links(document_directory(pages)).hrefs
        self.assertEqual(set(links),{url_path(n) for n in range(2,3466)})
        self.assertEqual(len(links),3464)
        self.assertIn('/page-404.html',links)
        self.assertNotIn('/404.html',links)

    def test_related_prefers_same_region_and_does_not_return_first_pages(self):
        pages=[dict(number=n,region='서울 강남구' if n<4 else '경기 수원시',topic='화분') for n in range(1,9)]
        self.assertEqual(Links(related_documents(pages,7,3)).hrefs,['/6.html','/8.html','/5.html'])
        self.assertEqual(Links(related_documents(pages[:1],1)).hrefs,[])
