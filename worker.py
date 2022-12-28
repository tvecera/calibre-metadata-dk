#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = "GPL v3"
__copyright__ = "2021, Tomas Vecera <tomas@vecera.dev>"
__docformat__ = "restructuredtext cs"

import re
import socket
from datetime import datetime
from threading import Thread

from calibre.utils.date import parse_date
from calibre.ebooks.metadata import check_isbn
from calibre.ebooks.metadata.book.base import Metadata
from calibre.library.comments import comments_to_html
from lxml import etree


class Worker(Thread):
    """
    Get book details from databazeknih.cz (DK) book page in a separate thread
    """

    def __init__(self, url, result_queue, browser, log, relevance, plugin, timeout=20):
        Thread.__init__(self)
        self.title = None
        self.isbn = None
        self.databazeknih_id = None
        self.daemon = True
        self.url = url
        self.result_queue = result_queue
        self.log = log
        self.languages = []
        self.timeout = timeout
        self.relevance = relevance
        self.plugin = plugin
        self.browser = browser.clone_browser()
        self.cover_url = None
        self.authors = []
        self.comments = None
        self.pubdate = None
        self.publisher = None
        self.series = None
        self.series_index = None
        self.tags = []
        self.rating = 0
        self.more_info = None
        self.lang_map = {}

        # Mapping language to something calibre understand. Just used in this plugin
        lm = {
            "eng": ("English", u"anglický"),
            "ces": ("Czech", u"český"),
        }
        for code, names in lm.items():
            for name in names:
                self.lang_map[name] = code

    def run(self):
        """
        """
        self.log.info("    Worker.run: self: ", self)
        try:
            self.get_details()
        except:
            self.log.exception("get_details() failed for url: %r" % self.url)

    def get_details(self):
        """
        """
        self.log.info("    Worker.get_details:")
        self.log.info("        self:     ", self)
        self.log.info("        self.url: ", self.url)

        root = self.fetch_url(self.url)
        if not root:
            self.log.exception("Cannot fetch / parse DK metadata for %r." % self.url)
            return

        self.more_info = self.fetch_more(root)

        self.parse_details(root)

    def fetch_url(self, url):
        """
        """
        try:
            self.log.info("        Fetch data for url: %r" % url)
            html = self.browser.open_novisit(url, timeout=self.timeout)
        except Exception as e:
            if callable(getattr(e, "getcode", None)) and e.getcode() == 404:
                self.log.exception("URL malformed: %r" % url)
                return
            attr = getattr(e, "args", [None])
            attr = attr if attr else [None]
            if isinstance(attr[0], socket.timeout):
                self.log.exception("DK metadata for %r timed out. Try again later." % url)
            else:
                self.log.exception("Failed to make details query: %r" % url)
            return

        # Parse html
        root = None
        try:
            parser = etree.HTMLParser()
            root = etree.parse(html, parser)
        except:
            self.log.exception("Error parsing HTML for %r" % url)

        # Check if the html code contains 404 / DK doesn't return HTTP status code 404
        header_node = root.xpath("//h1/text()")
        if header_node and (u"<h1>Stránka 404</h1>" in header_node[0]):
            self.log.error("URL malformed: %r" % url)
            return None

        return root

    def fetch_more(self, root):
        """
        """
        try:
            more_info_node = root.xpath("//span[@id='abinfo']/@bid")
            self.log.info("        Book bid: %s" % more_info_node)
            more_info_url = "https://www.databazeknih.cz/books/book-detail-more-info-ajax.php?bid=" + str(
                more_info_node[0])
            self.log.info("        More info url: %r" % more_info_url)
        except:
            self.log.info("Failed to fetch more info for url: %r" % self.url)
            return None

        return self.fetch_url(more_info_url)

    def parse_details(self, root):
        """
        """
        try:
            self.log.info("        Parse details: %r" % self.url)
            self.databazeknih_id = self.parse_databazeknih_id(self.url)
            self.log.info("        Parsed DK identifier: %s" % self.databazeknih_id)
        except:
            self.log.exception("Error parsing DK identifier for url: %r" % self.url)
            self.databazeknih_id = None

        # Parse title
        self.parse_title(root)
        # Parse authors
        self.parse_authors(root)
        if not self.title or not self.authors or not self.databazeknih_id:
            self.log.error("Could not find title/authors/DK id for %r" % self.url)
            self.log.error("DK id: %r Title: %r Authors: %r" % (self.databazeknih_id, self.title, self.authors))
            return

        mi = Metadata(self.title, self.authors)
        mi.set_identifier("databazeknih", self.databazeknih_id)

        # Parse series
        self.parse_series(root, mi)
        # Parse comments
        self.parse_comments(root, mi)
        # Parse publisher
        self.parse_publisher(root, mi)
        # Parse pubdate
        self.parse_pubdate(root, mi)
        # Parse tags
        self.parse_tags(root, mi)
        # Parse rating
        self.parse_rating(root, mi)
        # Parse book ISBN
        self.parse_isbn(self.more_info, mi)
        # Parse language
        self.parse_language(self.more_info, mi)
        # Parse book cover
        self.parse_cover(root, mi)

        mi.source_relevance = self.relevance

        self.log.info(mi)
        self.result_queue.put(mi)

    def parse_databazeknih_id(self, url):
        """
        """
        databazeknih_id_node = re.search("/knihy/(.*)", url).groups("0")[0]
        if databazeknih_id_node:
            return databazeknih_id_node
        else:
            return None

    def parse_title(self, root):
        """
        """
        try:
            title_node = root.xpath("//h1[@itemprop='name']/text()")
            self.log.info("        Title node: %s" % title_node)
            self.title = title_node[0].replace("&nbsp;", "").strip()
            self.log.info("        Parsed book title: %s" % self.title)
        except:
            self.log.exception("Error parsing title for url: %r" % self.url)
            self.title = None

    def parse_authors(self, root):
        """
        """
        try:
            author_nodes = root.xpath("//h2[@class='jmenaautoru']/span[@itemprop='author']/a/text()")
            self.log.info("        Author nodes: %s" % author_nodes)
            self.authors = []
            if author_nodes:
                for author in author_nodes:
                    self.log.info("        Author: %s" % author)
                    self.authors.append(u"".join(author))
            self.log.info("        Parsed authors: %s" % self.authors)
        except:
            self.log.exception("Error parsing authors for url: %r" % self.url)

    def parse_series(self, root, mi):
        """
        """
        try:
            series_node = root.xpath("//em[@class='info']/../a/text()")
            series_index_node = root.xpath("//em[@class='info']/text()")
            self.log.info("        Series node: %s" % series_node)
            self.log.info("        Series index node: %s" % series_index_node)

            if series_node:
                series_url = root.xpath("//em[@class='info']/../a/@href")
                self.log.info("        Series url node: %s" % series_url)
                if ("serie" in series_url[0]) and series_index_node:
                    index = re.search("(\d*)\.", series_index_node[0]).groups("0")[0]
                    self.log.info("        Series index: %s" % index)
                    try:
                        index = float(index)
                    except:
                        index = None
                    mi.series = self.series = series_node[0]
                    mi.series_index = self.series_index = index
            self.log.info("        Parsed series: %s" % self.series)
            self.log.info("        Parsed series index: %s" % self.series_index)
        except:
            self.log.exception("Error parsing series for url: %r" % self.url)

    def parse_comments(self, root, mi):
        """
        """
        try:
            comments_node = root.xpath("//p[@itemprop='description']/span/text()")
            if not comments_node:
                comments_node = root.xpath("//p[@itemprop='description']/text()")
            self.log.info("        Comments node: %s" % comments_node)

            if comments_node:
                mi.comments = self.comments = comments_to_html("\r\n".join(comments_node))
            self.log.info("        Parsed comments: %s" % mi.comments)
        except:
            self.log.exception("Error parsing comments for url: %r" % self.url)

    def parse_publisher(self, root, mi):
        """
        """
        try:
            publisher_node = root.xpath("//span[@itemprop='publisher']/a/text()")
            self.log.info("        Publisher node: %s" % publisher_node)

            if publisher_node:
                mi.publisher = self.publisher = publisher_node[0].strip()
            self.log.info("        Parsed publisher: %s" % mi.publisher)
        except:
            self.log.exception("Error parsing publisher for url: %r" % self.url)

    def parse_pubdate(self, root, mi):
        """
        """
        try:
            datepublished_node = root.xpath("//span[@itemprop='datePublished']/text()")
            self.log.info("        DatePublished node: %s" % datepublished_node)

            if datepublished_node:
                mi.pubdate = self.pubdate = parse_date(datepublished_node[0], assume_utc=True)
            self.log.info("        Parsed pubdate: %s" % mi.pubdate)
        except:
            self.log.exception("Error parsing pubdate for url: %r" % self.url)

    def parse_tags(self, root, mi):
        """
        """
        try:
            tag_nodes = root.xpath("//h5[@itemprop='genre']/a/text()")
            self.log.info("        Tag nodes: %s" % tag_nodes)

            if tag_nodes:
                for tag in tag_nodes:
                    self.tags.append(u"".join(tag))
            mi.tags = self.tags
            self.log.info("        Parsed tags: %s" % mi.tags)
        except:
            self.log.exception("Error parsing tags for url: %r" % self.url)

    def parse_rating(self, root, mi):
        """
        """
        try:
            rating_node = root.xpath("//a[@class='bpoints']/div/text()")
            self.log.info("        Rating node: %s" % rating_node)

            if rating_node:
                rating_node = rating_node[0].strip("%")
                rating_node = float(rating_node)
                self.log.info("        Rating_num: %s" % rating_node)

                if rating_node:
                    if rating_node >= 80:
                        self.rating = 5
                    elif rating_node >= 60:
                        self.rating = 4
                    elif rating_node >= 40:
                        self.rating = 3
                    elif rating_node >= 20:
                        self.rating = 2
                    elif rating_node >= 0:
                        self.rating = 1

            mi.rating = self.rating
            self.log.info("        Parsed rating: %s" % mi.rating)
        except:
            self.log.exception("Error parsing rating for url: %r" % self.url)

    def parse_isbn(self, root, mi):
        """
        """
        try:
            if self.more_info:
                isbn_node = root.xpath("//span[@itemprop='isbn']/text()")
                self.log.info("        ISBN node: %s" % isbn_node)
                if isbn_node:
                    self.isbn = check_isbn(isbn_node[0])
                self.log.info("        ISBN: %s" % self.isbn)
                if self.isbn and self.databazeknih_id:
                    mi.isbn = self.isbn
                    self.plugin.cache_isbn_to_identifier(self.isbn, self.databazeknih_id)
        except:
            self.log.exception("Error parsing ISBN for url: %r" % self.url)

    def parse_language(self, root, mi):
        """
        """
        try:
            if self.more_info:
                language_node = root.xpath("//span[@itemprop='language']/text()")
                self.log.info("        Language node: %s" % language_node)
                if language_node:
                    language = u"".join(language_node[0])
                    self.languages.append(self.lang_map.get(language, "ces"))
                self.log.info("        Language: %s" % ",".join(self.languages))
                mi.languages = self.languages
        except:
            self.log.exception("Error parsing languages for url: %r" % self.url)

    def parse_cover(self, root, mi):
        """
        """
        try:
            cover_url_node = root.xpath("//*[@id='icover_mid']//img[@class='kniha_img']/@src")
            self.log.info("        Cover url node: %s" % cover_url_node)
            if cover_url_node:
                self.cover_url = cover_url_node[0]
                self.plugin.cache_identifier_to_cover_url(self.databazeknih_id, self.cover_url)
                self.log.info("        Parsed URL for cover: %r" % self.cover_url)
            mi.has_cover = bool(self.cover_url)
        except:
            self.log.exception("Error parsing cover for url: %r" % self.url)
