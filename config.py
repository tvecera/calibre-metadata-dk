#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from calibre.gui2.metadata.config import ConfigWidget as DefaultConfigWidget
from calibre.utils.config import JSONConfig

__license__ = 'GPL v3'
__copyright__ = '2021, Tomas Vecera <tomas@vecera.dev>'
__docformat__ = 'restructuredtext cs'

from PyQt5 import Qt as QtGui
from PyQt5.Qt import QLabel, QGridLayout, Qt, QGroupBox, QCheckBox

STORE_NAME = 'Options'

KEY_PARSE_SERIES = 'parseSeries'
KEY_PARSE_COMMENTS = 'parseComments'
KEY_PARSE_RATING = 'parseRating'
KEY_ADD_DATABAZEKNIH_ID = 'addDatabazeKnihId'
KEY_VERBOSE_LOGGING = 'verboseLogging'

DEFAULT_STORE_VALUES = {
    KEY_PARSE_SERIES: True,
    KEY_PARSE_COMMENTS: True,
    KEY_PARSE_RATING: True,
    KEY_ADD_DATABAZEKNIH_ID: True,
    KEY_VERBOSE_LOGGING: False,
}

# This is where all preferences for this plugin will be stored
plugin_prefs = JSONConfig('plugins/DatabazeKnihCZ')

# Set defaults
plugin_prefs.defaults[STORE_NAME] = DEFAULT_STORE_VALUES


class ConfigWidget(DefaultConfigWidget):
    """
    """
    def __init__(self, plugin):
        DefaultConfigWidget.__init__(self, plugin)
        c = plugin_prefs[STORE_NAME]

        other_group_box = QGroupBox('Other options', self)
        self.l.addWidget(other_group_box, self.l.rowCount(), 0, 1, 2)
        other_group_box_layout = QGridLayout()
        other_group_box.setLayout(other_group_box_layout)

        index = 0

        # Parse Series - KEY_PARSE_SERIES
        parse_series_label = QLabel('Načtení názvu knižní série a pořadí:', self)
        parse_series_label.setToolTip('Při vybrání této položky se plugin bude snažit dotáhnout informaci o \n'
                                      'knižní sérii a pořadí knihy v dané sérii.\n'
                                      'S ohledem na strukturu stránek databazeknih.cz není moc spolehlivé !!!\n'
                                      )
        other_group_box_layout.addWidget(parse_series_label, index, 0, 1, 1)

        self.parse_series_checkbox = QtGui.QCheckBox(self)
        self.parse_series_checkbox.setChecked(c.get(KEY_PARSE_SERIES, DEFAULT_STORE_VALUES[KEY_PARSE_SERIES]))
        other_group_box_layout.addWidget(self.parse_series_checkbox, index, 1, 1, 1)
        index += 1

        # Parse comments - KEY_PARSE_COMMENTS
        parse_comments_label = QLabel('Načtení popisu knihy:', self)
        parse_comments_label.setToolTip('Při vybrání této položky se plugin bude snažit dotáhnout popis\n'
                                        'knižního titulu. V calibre označován jako komentáře.\n'
                                        )
        other_group_box_layout.addWidget(parse_comments_label, index, 0, 1, 1)

        self.parse_comments_checkbox = QtGui.QCheckBox(self)
        self.parse_comments_checkbox.setChecked(c.get(KEY_PARSE_COMMENTS, DEFAULT_STORE_VALUES[KEY_PARSE_COMMENTS]))
        other_group_box_layout.addWidget(self.parse_comments_checkbox, index, 1, 1, 1)
        index += 1

        # Parse rating - KEY_PARSE_RATING
        parse_rating_label = QLabel('Načtení hodnocení knihy:', self)
        parse_rating_label.setToolTip('Při vybrání této položky se plugin bude snažit dotáhnout hodnocení knihy.\n'
                                      )
        other_group_box_layout.addWidget(parse_rating_label, index, 0, 1, 1)

        self.parse_rating_checkbox = QtGui.QCheckBox(self)
        self.parse_rating_checkbox.setChecked(c.get(KEY_PARSE_RATING, DEFAULT_STORE_VALUES[KEY_PARSE_RATING]))
        other_group_box_layout.addWidget(self.parse_rating_checkbox, index, 1, 1, 1)
        index += 1

        # Add databazeknih ID to book identificators - KEY_ADD_DATABAZEKNIH_ID
        add_databazeknih_id_label = QLabel('Vložit identifikátor z databáze knih:', self)
        add_databazeknih_id_label.setToolTip('Při vybrání této položky plugin vloží mezi knižní identifikátory\n'
                                             'identifikátor Databazeknih.cz. Např. aristokratka-posledni-aristokratka-134832.\n'
                                             )
        other_group_box_layout.addWidget(add_databazeknih_id_label, index, 0, 1, 1)

        self.add_databazeknih_id_checkbox = QtGui.QCheckBox(self)
        self.add_databazeknih_id_checkbox.setChecked(
            c.get(KEY_ADD_DATABAZEKNIH_ID, DEFAULT_STORE_VALUES[KEY_ADD_DATABAZEKNIH_ID]))
        other_group_box_layout.addWidget(self.add_databazeknih_id_checkbox, index, 1, 1, 1)
        index += 1

        # Verbose logging KEY_VERBOSE_LOGGING
        verbose_loging_label = QLabel('Zapnot podrobné logování:', self)
        verbose_loging_label.setToolTip('Při vybrání této volby bude plugin logovat více informací.\n'
                                        'Slouží pro případnou identifikaci problému, chyby.\n'
                                        )
        other_group_box_layout.addWidget(verbose_loging_label, index, 0, 1, 1)

        self.verbose_loging_label_checkbox = QtGui.QCheckBox(self)
        self.verbose_loging_label_checkbox.setChecked(
            c.get(KEY_VERBOSE_LOGGING, DEFAULT_STORE_VALUES[KEY_VERBOSE_LOGGING]))
        other_group_box_layout.addWidget(self.verbose_loging_label_checkbox, index, 1, 1, 1)
        index += 1

    def commit(self):
        DefaultConfigWidget.commit(self)
        new_prefs = {KEY_PARSE_SERIES: self.parse_series_checkbox.isChecked(),
                     KEY_PARSE_COMMENTS: self.parse_comments_checkbox.isChecked(),
                     KEY_PARSE_RATING: self.parse_rating_checkbox.isChecked(),
                     KEY_ADD_DATABAZEKNIH_ID: self.add_databazeknih_id_checkbox.isChecked(),
                     KEY_VERBOSE_LOGGING: self.verbose_loging_label_checkbox.isChecked()}

        plugin_prefs[STORE_NAME] = new_prefs
