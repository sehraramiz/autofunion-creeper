# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from BeautifulSoup import BeautifulSoup

import time
import config


class Pershiess:
    def __init__(self, args):
        self.username = args["username"] or config.USERNAME
        self.password = args["password"] or config.PASSWORD

    def start(self):
        self.browser = webdriver.Chrome()
        self.browser.get(config.URL)
        self._login()
        self._select_current_semester()

    def _login(self):
        id_box = self.browser.find_element_by_id('edId')
        id_box.clear()
        id_box.send_keys(self.username)
        pass_box = self.browser.find_element_by_id('edPass')
        pass_box.clear()
        pass_box.send_keys(self.password)

        # login with captcha
        # just enter the code and wait
        # time.sleep(10)

        enter_button = self.browser.find_element_by_id('edEnter')
        enter_button.click()
        try:
            self.browser.find_element_by_id('edHomePage').click()
        except Exception as e:
            pass

    # select current semester in main page
    def _select_current_semester(self):
        sem_soup = BeautifulSoup(self.browser.page_source)
        sem_list = sem_soup.find(attrs={'id': 'edSemester'}).findAll("option")
        select = Select(self.browser.find_element_by_id('edSemester'))
        # select semester by semester id
        select.select_by_value(sem_list[1]["value"])
        time.sleep(0.2)
