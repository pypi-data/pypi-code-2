import selenium_driver

_driver = None

def getDriver():
    global _driver
    if not _driver:
        _driver = selenium_driver.SeleniumDriver()
    return _driver