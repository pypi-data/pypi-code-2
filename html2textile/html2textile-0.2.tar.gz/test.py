# -*- coding: utf-8 -*-

# Copyright (c) 2010, Webreactor - Marcin Lulek <info@webreactor.eu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#simple test

from html2textile import html2textile

html = """<h2 style="color:green;">This is &amp; a title</h2>
<h3>This is a subhead</h3>
    <p style="color:red;">This is some text of dubious character. Isn&#8217;t the use of &#8220;quotes&#8221; just lazy writing &#8212; and theft of &#8216;intellectual property&#8217; besides? I think the time has come to see a block quote.</p>
    
    <blockquote lang="fr">
        <p lang="fr">This is a block quote. I&#8217;ll admit it&#8217;s not the most exciting block quote ever devised.</p>
    </blockquote>
    
    <p>Simple list:</p>

    <ol style="color:blue;">
        <li>one</li>
        <li>two</li>
        <li>three</li>
    </ol>

    <p>Multi-level list:</p>

    <ol>
        <li>one
    <ol>
        <li>aye</li>
        <li>bee</li>
        <li>see</li>
    </ol></li>
        <li>two
    <ol>
        <li>x</li>
        <li>y</li>
    </ol></li>
        <li>three</li>
    </ol>

    <p>Mixed list:</p>

    <ul>
        <li>Point one</li>
        <li>Point two
    <ol>
        <li>Step 1</li>
        <li>Step 2</li>
        <li>Step 3</li>
    </ol></li>
        <li>Point three
    <ul>
        <li>Sub point 1</li>
        <li>Sub point 2</li>
    </ul></li>
    </ul>

    <p>Well, that went well. How about we insert an <a href="/" title="watch out">old-fashioned hypertext link</a>? Will the quote marks in the tags get messed up? No!</p>

    <p><a href="http://www.textism.com" title="optional title">This is a link</a></p>

    <table style="border:1px solid black;">
        <tr>
            <th>this</th>
            <th>is</th>
            <th>a</th>
            <th>header</th>
        </tr>
        <tr style="background:gray;text-align:left;">
            <td colspan="2">this is</td>
            <td style="background:red;width:200px;">a</td>
            <td style="vertical-align:top;height:200px;text-align:justify;">row</td>
        </tr>
        <tr>
            <td>this</td>
            <td style="padding:10px;text-align:justify;">is</td>
            <td style="vertical-align:top;">another</td>
            <td class="bob" id="bob">row</td>
        </tr>
    </table>

    <p>An image:</p>

    <p><img src="/common/textist.gif" title="optional alt text" alt="optional alt text" /></p>

    <ol>
        <li>Librarians rule</li>
        <li>Yes they do</li>
        <li>But you knew that</li>
    </ol>

    <p>Some more text of dubious character. Here is a noisome string of <span class="caps">CAPITAL</span> letters. Here is something we want to <em>emphasize</em>. <br />
That was a linebreak. And something to indicate <strong>strength</strong>. Of course I could use <em>my own <span class="caps">HTML</span> tags</em> if I <strong>felt</strong> like it.</p>

    <h3>Coding</h3>

    <p>This <code>is some code, &#34;isn&#39;t it&#34;</code>. Watch those quote marks! Now for some preformatted text:</p>

    <p><pre><br />
<code>
    $text = str_replace(&#8221;<p><span>::</span></p>&#8220;,&#8221;&#8220;,$text);
    $text = str_replace(&#8221;<span>::</span></p>&#8220;,&#8221;&#8220;,$text);
    $text = str_replace(&#8221;<span>::</span>&#8220;,&#8221;&#8220;,$text);</p>

    <p></code><br />
</pre></p>

    <p>This isn&#8217;t code.</p>

    <p>So you see, my friends:</p>

    <ul>
        <li>The time is now</li>
        <li>The time is not later</li>
        <li>The time is not yesterday</li>
        <li>We must act</li>
    </ul>"""

print html2textile(html)
#result
r = """
h2{color:green}. This is a title

h3. This is a subhead

p{color:red}. This is some text of dubious character. Isn’t the use of“quotes”just lazy writing—and theft of‘intellectual property’besides? I think the time has come to see a block quote.

bq[fr]. 
p[fr]. This is a block quote. I’ll admit it’s not the most exciting block quote ever devised.

Simple list:

# one
# two
# three

Multi-level list:

# one
## aye
## bee
## see
# two
## x
## y
# three

Mixed list:

* Point one
* Point two
## Step 1
## Step 2
## Step 3
* Point three
** Sub point 1
** Sub point 2

Well, that went well. How about we insert an "old-fashioned hypertext link (watch out)":/ ? Will the quote marks in the tags get messed up? No!

 "This is a link (optional title)":http://www.textism.com 

{border:1px solid black}

this
is
a
header
{background:gray;text-align:left}
this is
{background:red;width:200px}a
{vertical-align:top;height:200px;text-align:justify}row

this
{padding:10px;text-align:justify}is
{vertical-align:top}another
(#bob)(bob)row
An image:

 !/common/textist.gif(optional alt text)!

# Librarians rule
# Yes they do
# But you knew that

Some more text of dubious character. Here is a noisome string of %(caps)CAPITAL% letters. Here is something we want to _emphasize_ .
That was a linebreak. And something to indicate *strength* . Of course I could use _my own %(caps)HTML% tags_ if I *felt* like it.

h3. Coding

This
is some code,"isn't it". Watch those quote marks! Now for some preformatted text:





$text = str_replace(”
 %::% 
“,”“,$text);
    $text = str_replace(” %::% “,”“,$text);
    $text = str_replace(” %::% “,”“,$text);



This isn’t code.

So you see, my friends:

* The time is now
* The time is not later
* The time is not yesterday
* We must act
"""