#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = "GPL v3"
__copyright__ = "2021, Tomas Vecera <tomas@vecera.dev>"
__docformat__ = "restructuredtext cs"

import re
import time
from queue import Empty, Queue
from urllib.parse import quote

from calibre.ebooks.metadata import check_isbn
from calibre.ebooks.metadata.sources.base import Source
from html5_parser import parse


class DatabazeKnihCZ(Source):
    """
    """
    name = "DatabazeKnihCZ"
    description = "Downloads metadata and covers from databazeknih.cz based on title and author"
    supported_platforms = ["windows", "osx", "linux"]
    author = "Tomas Vecera <tomas@vecera.dev>"
    version = (0, 9, 1)
    minimum_calibre_version = (5, 0, 1)

    capabilities = frozenset(["identify", "cover"])
    touched_fields = frozenset(
        ["title", "authors", "publisher", "pubdate", "languages", "tags", "rating", "series", "series_index",
         "comments",
         "identifier:databazeknih", "identifier:isbn"])

    has_html_comments = True
    supports_gzip_transfer_encoding = False
    can_get_multiple_covers = False
    cached_cover_url_is_reliable = True
    prefer_results_with_isbn = False

    ID_NAME = "databazeknih"
    BASE_URL = "https://www.databazeknih.cz/"
    GOOGLE_BASE_URL = "https://www.google.com/search?q=site:databazeknih.cz "

    def config_widget(self):
        """
        """
        from calibre_plugins.databazeknihcz.config import ConfigWidget
        return ConfigWidget(self)

    def load_config(self):
        import calibre_plugins.databazeknihcz.config as cfg

        self.cfg_parse_series = cfg.plugin_prefs[cfg.STORE_NAME].get(cfg.KEY_PARSE_SERIES, True)
        self.cfg_parse_comments = cfg.plugin_prefs[cfg.STORE_NAME].get(cfg.KEY_PARSE_COMMENTS, True)
        self.cfg_parse_rating = cfg.plugin_prefs[cfg.STORE_NAME].get(cfg.KEY_PARSE_RATING, True)
        self.cfg_add_databazeknih_id = cfg.plugin_prefs[cfg.STORE_NAME].get(cfg.KEY_ADD_DATABAZEKNIH_ID, True)
        self.cfg_verbose_loging = cfg.plugin_prefs[cfg.STORE_NAME].get(cfg.KEY_VERBOSE_LOGGING, True)

    def is_customizable(self):
        """
        """
        return True

    def identify(self, log, result_queue, abort, title=None, authors=None, identifiers=None, timeout=30):
        """
        Note this method will retry without identifiers automatically if no match is found with identifiers.
        """
        if identifiers is None:
            identifiers = {}
        self.load_config()

        # Create matches lists
        matches = []

        book_id = identifiers.get("databazeknih", None)
        log.info("Matching with DK ID: %s" % book_id)
        if book_id:
            databazeknih_url = DatabazeKnihCZ.BASE_URL + "knihy/" + book_id
            log.info("Found DK URL: %s" % databazeknih_url)
            matches.append(databazeknih_url)

        # Initialize browser object
        br = self.browser

        log.info("Google - matching with Title: %s & Author(s): %s" % (title, authors))
        if title:
            # Get matches for only title
            search_title = title.replace(" ", "+").replace("-", "+")
            google_url = "%s" % search_title
            if title and authors:
                search_author = authors[0].replace(" ", "+")
                # Get matches for title + author
                google_url = "%s+%s" % (search_author, search_title)

            # Remove multiple "+" from Google search query
            google_url = quote(re.sub(r"\+{2,}", "+", google_url).encode("utf8"))
            google_url = "%s%s" % (DatabazeKnihCZ.GOOGLE_BASE_URL, google_url)
            log.info("Google search URL: %r" % google_url)
            google_raw = br.open_novisit(google_url, timeout=timeout).read().strip()
            google_root = parse(google_raw)
            google_nodes = google_root.xpath("(//div[@class='g'])//a/@href")

            for url in google_nodes[:2]:
                if url != "#":
                    matches.append(url)

        # Return if no Title
        if abort.is_set():
            return

        # Report the matches
        log.info("Matches are: ", matches)

        # Setup worker thread
        from calibre_plugins.databazeknihcz.worker import Worker
        workers = [Worker(url, result_queue, br, log, i, self) for i, url in enumerate(matches)]

        # Start working
        for w in workers:
            w.start()
            # Delay a little for every worker
            time.sleep(1)

        while not abort.is_set():
            a_worker_is_alive = False
            for w in workers:
                w.join(0.2)
                if abort.is_set():
                    break
                if w.is_alive():
                    a_worker_is_alive = True
            if not a_worker_is_alive:
                break

        return None

    def get_cached_cover_url(self, identifiers):
        """
        """
        book_id = identifiers.get("databazeknih", None)
        if book_id is None:
            book_id = check_isbn(identifiers.get("isbn", None))

        url = self.cached_identifier_to_cover_url(book_id)
        return url

    def download_cover(self, log, result_queue, abort, title=None, authors=None, identifiers=None, timeout=30):
        """
        """
        if identifiers is None:
            identifiers = {}
        cached_url = self.get_cached_cover_url(identifiers)

        if not cached_url:
            log.info("No cached cover found, running identify")
            rq = Queue()
            self.identify(log, rq, abort, title=title, authors=authors, identifiers=identifiers)
            if abort.is_set():
                return
            results = []
            while True:
                try:
                    results.append(rq.get_nowait())
                except Empty:
                    break
            results.sort(key=self.identify_results_keygen(title=title, authors=authors, identifiers=identifiers))
            for mi in results:
                cached_url = self.get_cached_cover_url(mi.identifiers)
                if cached_url:
                    break
        if cached_url is None:
            log.info("No cover found")
            return

        if abort.is_set():
            return
        br = self.browser
        log.info("Downloading cover from:", cached_url)
        try:
            cdata = br.open_novisit(cached_url, timeout=timeout).read()
            result_queue.put((self, cdata))
        except:
            log.exception("Failed to download cover from:", cached_url)
