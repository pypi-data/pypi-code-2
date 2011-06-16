from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.pdfjs import pdfjsMessageFactory as _
from collective.pdfjs.browser.interfaces import IInlinePDFView

JAVASCRIPT_TEMPLATE = """\
        function queryParams() {
            var qs = window.location.search.substring(1);
            var kvs = qs.split("&");
            var params = { };
            for (var i = 0; i < kvs.length; ++i) {
                var kv = kvs[i].split("=");
                params[unescape(kv[0])] = unescape(kv[1]);
            }
            return params;
        }

        var canvas, numPages, pageDisplay, pageNum;
        function load() {
            canvas = document.getElementById("canvas");
            canvas.mozOpaque = true;
            pageDisplay = document.getElementById("pageNumber");
            pageNum = parseInt(queryParams().page) || 1;
            fileName = queryParams().file || "@@FILE_ABSOLUTE_URL@@";
            open(fileName);
        }

        function open(url) {
            document.title = url;
            req = new XMLHttpRequest();
            req.open("GET", url);
            req.mozResponseType = req.responseType = "arraybuffer";
            req.expected = (document.URL.indexOf("file:") == 0) ? 0 : 200;
            req.onreadystatechange = xhrstate;
            req.send(null);
        }

        function xhrstate() {
            if (req.readyState == 4 && req.status == req.expected) {
                var data = req.mozResponseArrayBuffer ||
                           req.mozResponse ||
                           req.responseArrayBuffer ||
                           req.response;
                pdf = new PDFDoc(new Stream(data));
                numPages = pdf.numPages;
                document.getElementById("numPages").innerHTML = numPages.toString();
                gotoPage(pageNum);
            }
        }

        function displayPage(num) {
            pageDisplay.value = num;

            var t0 = Date.now();

            var page = pdf.getPage(pageNum = num);

            var t1 = Date.now();

            var ctx = canvas.getContext("2d");
            ctx.save();
            ctx.fillStyle = "rgb(255, 255, 255)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.restore();

            var gfx = new CanvasGraphics(ctx);

            // page.compile will collect all fonts for us, once we have loaded them
            // we can trigger the actual page rendering with page.display
            var fonts = [];
            page.compile(gfx, fonts);

            var t2 = Date.now();

            // This should be called when font loading is complete
            page.display(gfx);

            var t3 = Date.now();

        }

        function nextPage() {
            if (pageNum < numPages)
                ++pageNum;
            displayPage(pageNum);
        }

        function prevPage() {
            if (pageNum > 1)
                --pageNum;
            displayPage(pageNum);
        }
        function gotoPage(num) {
            if (0 <= num && num <= numPages)
                pageNum = num;
            displayPage(pageNum);
        }
"""

class JavaScript(BrowserView):
    """
    Returns the reader javascript.
    """

    def __call__(self, request=None, response=None):
        self.request.response.setHeader("Content-type", "text/javascript")
        ref_path = self.request.HTTP_REFERER.split('/')
        dl_path = ["at_download", "file"]
        file_url = "/".join((ref_path[:-1] + dl_path))
        import pdb; pdb.set_trace()
        return JAVASCRIPT_TEMPLATE.replace("@@FILE_ABSOLUTE_URL@@", file_url )

class InlinePDFView(BrowserView):
    """
    Inline PDF View browser view
    """
    implements(IInlinePDFView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
