from BeautifulSoup import BeautifulSoup

def remove_tags(html, *tags):
    soup = BeautifulSoup(html)
    for tag in tags:
        for tag in soup.findAll(tag):
            tag.replaceWith("")

    return str(soup)
