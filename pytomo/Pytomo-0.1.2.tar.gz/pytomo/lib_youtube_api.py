#!/usr/bin/env python
"""Function to get the most popular Youtube videos according to the time frame.
    Arguments:
        time = 'today' or 'month' or 'week' or all_time'
        max_results : In multiples of 25
    Returns: A list containing the list of videos.
"""

from pytomo.lib_cache_url import get_all_links
import pytomo.config_pytomo as config_pytomo

# Youtube webpage limitation
MAX_VIDEO_PER_PAGE = 25

def get_popular_links(time=config_pytomo.TIME_FRAME,
                      max_results=config_pytomo.MAX_PER_PAGE):
    """Returns the most popular youtube links (world-wide).
    The number of videos returned is given as Total_pages.
    (The results returned are in no particular order).
    A set of only Youtube links from url
    """
    config_pytomo.LOG.debug('Getting popular links')
    if time == 'today':
        time_frame = 't'
    elif time == 'week':
        time_frame = 'w'
    elif time == 'month':
        time_frame = 'm'
    elif time == 'all_time':
        time_frame = 'a'
    else:
        config_pytomo.LOG.info('Time frame not recognised. '
                               'Assuming All time Popular videos.')
        time_frame = 'a'
    if max_results > MAX_VIDEO_PER_PAGE:
        pages = int(max_results) / MAX_VIDEO_PER_PAGE
    else:
        pages = 1
    for page in xrange(pages):
        url = ''.join(
            ('http://www.youtube.com/charts/videos_views?p=2&gl=US&t=',
             time_frame, '&p=', str(page + 1))
                     )
        links = get_all_links(url)
        if not links:
            config_pytomo.LOG.warning('No popular link was found')
        popular_links = set()
        for link in links:
            if link.find("/watch") >= 0:
                if link.startswith('/'):
                    link = ''.join(("http://www.youtube.com", link))
                popular_links.add(link)
                if len(popular_links) >= max_results:
                    break
    return popular_links

