# -*- coding: utf-8 -*-


# navigation functions
def perform(browser, action):
    script = 'return Perform("' + action + '")'
    browser.execute_script(script)


def perform_std(browser, way):
    script = "return PerformStd('" + way + "')"
    browser.execute_script(script)


def back(browser):
    browser.execute_script('try{Exit();}catch(e){}')
    pass
