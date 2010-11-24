from trac_tickets.alchemy import *
from pylab import *

def prep_figure(title, x_label, y_label):
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    fig.autofmt_xdate(rotation=45)
    return (ax, canvas)

def render_canvas(canvas, format):
    canvas.draw()
    size = canvas.get_renderer().get_canvas_width_height()
    buf = canvas.tostring_rgb()
    im = Image.fromstring('RGB', size, buf, 'raw', 'RGB', 0, 1)
    imdata = StringIO()
    im.save(imdata, format=format)
    return imdata.getvalue()

def graph_hours_sum(authors, format='JPEG'):
    """ Returns data for a graph of hour sums"""
    ax, canvas = prep_figure(title='Developer Hour Sums',
                                 x_label='time',
                                                     y_label='hours commited')
    styles = ['g-','r-','b-', 'k-', 'c-', 'm-', 'y-' ]
    for i, author in enumerate(authors):
        dates = []
        hours = []
        sums = []
        sum = 0
        for day in session.query(DayAuthorHoursSummary).filter("author='%s'" % author).order_by('date').all():
            sum = sum + float(day.hours)
            sums.append(sum)
            dates.append(date2num(day.date))
            hours.append(float(day.hours))
        hours = hours[1:-1]
        dates = dates[1:-1]
        sums = sums[1:-1]
        if len(dates) != 0:
            ax.plot_date(dates, sums, styles[i % len(styles)], label=author)
    session.close()
    return render_canvas(canvas, format)


def graph_developer_hour_commits(author, format='JPEG'):
    """ Returns a scatter plot of a developer's commited hours"""
    ax, canvas = prep_figure(
        title='Commit Hours: %s' % author,
        x_label='time',
        y_label='hours commited',
    )
    dates = []
    hours = []
    for day in session.query(DayAuthorHoursSummary).filter(
      "author='%s'" % author).order_by('date').all():
        dates.append(date2num(day.date))
        hours.append(float(day.hours))
    session.close()
    if len(dates) != 0:
        ax.plot_date(dates, hours, 'go', label=author)
    return render_canvas(canvas, format)


def graph_account_sum(account, format='JPEG'):
    ax, canvas = prep_figure(
        title='%s' % account.name,
        x_label='time',
        y_label='account input sum',
    )
    sums = []
    dates = []
    for transaction in account.get_table()[2]:
        sums.append(transaction[-1])
        dates.append(date2num(transaction[0]))
    if len(dates) != 0:
        ax.plot_date(dates, sums, '-')
    return render_canvas(canvas, format)
