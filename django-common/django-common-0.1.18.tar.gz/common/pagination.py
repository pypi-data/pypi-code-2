from django.core.paginator import Paginator, EmptyPage, InvalidPage

from common.templatetags.common_tags import alter_qs


def paginate(qs, request, per_page=15, frame_size=5):
    try:    
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    paginator = Paginator(qs, per_page)
    try:    
        page = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        page_number = 1
        page = paginator.page(1)
    query_string = request.META['QUERY_STRING']

    if page.has_previous():
        page.previous_page_url = alter_qs(query_string, 'page', page.previous_page_number())
    else:
        page.previous_page_url = None

    if page.has_next():
        page.next_page_url = alter_qs(query_string, 'page', page.next_page_number())
    else:
        page.next_page_url = None

    page.first_page_url = alter_qs(query_string, 'page', 1)
    page.last_page_url = alter_qs(query_string, 'page', page.paginator.num_pages)

    urls = []
    if frame_size is None:
        for x in page.paginator.page_range:
            urls.append((x, alter_qs(query_string, 'page', x)))
        start = 1
        end = page.paginator.page_range
    else:
        half = int(frame_size / 2.0)
        start = max(1, page.number - int(frame_size / 2.0))
        stop = min(page.paginator.num_pages, start + frame_size - 1)
        if stop == page.paginator.num_pages:
            if stop - start < (frame_size - 1):
                start = max(1, stop - frame_size)
        if start == 1:
            if stop - start < (frame_size - 1):
                stop = min(page.paginator.num_pages, start + frame_size)
        for x in xrange(start, stop + 1):
            urls.append((x, alter_qs(query_string, 'page', x)))
    page.paginator.frame = urls
    page.paginator.frame_start_page = start
    page.paginator.frame_end_page = stop

    return page
