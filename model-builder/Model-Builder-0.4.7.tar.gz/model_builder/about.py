#Boa:Dialog:wxDialog1
#import wxversion

import wx
import wx.html
import webbrowser
from __version__ import version


def create(parent):
    return wxDialog1(parent)

[wxID_WXDIALOG1, wxID_WXDIALOG1CLOSE, wxID_WXDIALOG1HTMLWINDOW1,
 wxID_WXDIALOG1TUTORIAL,
] = [wx.NewId() for _init_ctrls in range(4)]

class wxDialog1(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WXDIALOG1, name='', parent=prnt,
              pos=wx.Point(554, 80), size=wx.Size(357, 508),
              style=wx.DEFAULT_DIALOG_STYLE, title='About')
        self.SetClientSize(wx.Size(357, 508))

        self.htmlWindow1 = wx.html.HtmlWindow(id=wxID_WXDIALOG1HTMLWINDOW1,
              name='htmlWindow1', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(344, 464),
              style=wx.html.HW_SCROLLBAR_AUTO | wx.html.HW_DEFAULT_STYLE)
        self.htmlWindow1.SetThemeEnabled(True)
        self.htmlWindow1.SetToolTipString('About ModelBuilder')
        self.htmlWindow1.SetBackgroundColour(wx.Colour(255, 0, 0))

        self.close = wx.Button(id=wxID_WXDIALOG1CLOSE, label='Close',
              name='close', parent=self, pos=wx.Point(272, 482),
              size=wx.Size(80, 22), style=0)
        self.close.Bind(wx.EVT_BUTTON, self.OnCloseButton,
              id=wxID_WXDIALOG1CLOSE)

        self.tutorial = wx.Button(id=wxID_WXDIALOG1TUTORIAL, label='Tutorial',
              name='tutorial', parent=self, pos=wx.Point(8, 480),
              size=wx.Size(80, 22), style=0)
        self.tutorial.Bind(wx.EVT_BUTTON, self.OnTutorialButton,
              id=wxID_WXDIALOG1TUTORIAL)

    def __init__(self, parent):
        self._init_ctrls(parent)
        page = r"""
<html>
<head>


  <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">


  <title>About Model Builder</title>
</head>


<body>

<table style="width: 100%; text-align: left;" border="0" cellpadding="2" cellspacing="2">

  <tbody>

    <tr>

      <td style="text-align: center; vertical-align: middle;">

      <div style="text-align: center;">Model-Builder """+version+"""<br>

February, 2010<br>

      </div>

      <br>

      </td>

      <td style="vertical-align: top;"><img src="http://farm2.static.flickr.com/1354/1447948647_30e73ed6fa.jpg" title="" alt="" style="width: 100px; height: 100px;"><br>

      </td>

    </tr>


  </tbody>
</table>

ModelBuilder was originally developed and is maintained by Fl&aacute;vio
Code&ccedil;o Coelho &lt;fccoelho@fiocruz.br&gt;.<br>

<br>

Current Development team is composed by:<br>
<ul>
  <li>Fl&aacute;vio Code&ccedil;o Coelho (Main code and Bayesian Melding module)&nbsp;</li>
  <li>Antonio Pacheco (sensitivity analysis module)</li>
  <li>Claudia Torres Code&ccedil;o (tester)</li>
</ul>

<h3>Acknowledgements</h3>
<ul>
    <li> Thanks to Varun Hiremath for packaging Model Builder for Debian.
</ul>
<br><br>
A tutorial to ModelBuilder can be accessed by pressing the Tutorial
button below.<br>
<br>
For more information go to Model Buider's <a href="http://model-builder.sourceforge.net">website</a>
</body>
</html>
"""
        self.htmlWindow1.SetPage(page)

    def OnCloseButton(self, event):
        self.Close()

    def OnTutorialButton(self, event):
        webbrowser.open_new('http://model-builder.sourceforge.net')
