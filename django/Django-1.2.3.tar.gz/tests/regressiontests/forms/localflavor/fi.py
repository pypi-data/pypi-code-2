# -*- coding: utf-8 -*-
# Tests for the contrib/localflavor/ FI form fields.

tests = r"""
# FIZipCodeField #############################################################

FIZipCodeField validates that the data is a valid FI zipcode.
>>> from django.contrib.localflavor.fi.forms import FIZipCodeField
>>> f = FIZipCodeField()
>>> f.clean('20540')
u'20540'
>>> f.clean('20101')
u'20101'
>>> f.clean('20s40')
Traceback (most recent call last):
...
ValidationError: [u'Enter a zip code in the format XXXXX.']
>>> f.clean('205401')
Traceback (most recent call last):
...
ValidationError: [u'Enter a zip code in the format XXXXX.']
>>> f.clean(None)
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']
>>> f.clean('')
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']

>>> f = FIZipCodeField(required=False)
>>> f.clean('20540')
u'20540'
>>> f.clean('20101')
u'20101'
>>> f.clean('20s40')
Traceback (most recent call last):
...
ValidationError: [u'Enter a zip code in the format XXXXX.']
>>> f.clean('205401')
Traceback (most recent call last):
...
ValidationError: [u'Enter a zip code in the format XXXXX.']
>>> f.clean(None)
u''
>>> f.clean('')
u''

# FIMunicipalitySelect ###############################################################

A Select widget that uses a list of Finnish municipalities as its choices.
>>> from django.contrib.localflavor.fi.forms import FIMunicipalitySelect
>>> w = FIMunicipalitySelect()
>>> unicode(w.render('municipalities', 'turku'))
u'<select name="municipalities">
<option value="akaa">Akaa</option>
<option value="alajarvi">Alaj\xe4rvi</option>
<option value="alavieska">Alavieska</option>
<option value="alavus">Alavus</option>
<option value="artjarvi">Artj\xe4rvi</option>
<option value="asikkala">Asikkala</option>
<option value="askola">Askola</option>
<option value="aura">Aura</option>
<option value="brando">Br\xe4nd\xf6</option>
<option value="eckero">Ecker\xf6</option>
<option value="enonkoski">Enonkoski</option>
<option value="enontekio">Enonteki\xf6</option>
<option value="espoo">Espoo</option>
<option value="eura">Eura</option>
<option value="eurajoki">Eurajoki</option>
<option value="evijarvi">Evij\xe4rvi</option>
<option value="finstrom">Finstr\xf6m</option>
<option value="forssa">Forssa</option>
<option value="foglo">F\xf6gl\xf6</option>
<option value="geta">Geta</option>
<option value="haapajarvi">Haapaj\xe4rvi</option>
<option value="haapavesi">Haapavesi</option>
<option value="hailuoto">Hailuoto</option>
<option value="halsua">Halsua</option>
<option value="hamina">Hamina</option>
<option value="hammarland">Hammarland</option>
<option value="hankasalmi">Hankasalmi</option>
<option value="hanko">Hanko</option>
<option value="harjavalta">Harjavalta</option>
<option value="hartola">Hartola</option>
<option value="hattula">Hattula</option>
<option value="haukipudas">Haukipudas</option>
<option value="hausjarvi">Hausj\xe4rvi</option>
<option value="heinola">Heinola</option>
<option value="heinavesi">Hein\xe4vesi</option>
<option value="helsinki">Helsinki</option>
<option value="hirvensalmi">Hirvensalmi</option>
<option value="hollola">Hollola</option>
<option value="honkajoki">Honkajoki</option>
<option value="huittinen">Huittinen</option>
<option value="humppila">Humppila</option>
<option value="hyrynsalmi">Hyrynsalmi</option>
<option value="hyvinkaa">Hyvink\xe4\xe4</option>
<option value="hameenkoski">H\xe4meenkoski</option>
<option value="hameenkyro">H\xe4meenkyr\xf6</option>
<option value="hameenlinna">H\xe4meenlinna</option>
<option value="ii">Ii</option>
<option value="iisalmi">Iisalmi</option>
<option value="iitti">Iitti</option>
<option value="ikaalinen">Ikaalinen</option>
<option value="ilmajoki">Ilmajoki</option>
<option value="ilomantsi">Ilomantsi</option>
<option value="imatra">Imatra</option>
<option value="inari">Inari</option>
<option value="inkoo">Inkoo</option>
<option value="isojoki">Isojoki</option>
<option value="isokyro">Isokyr\xf6</option>
<option value="jalasjarvi">Jalasj\xe4rvi</option>
<option value="janakkala">Janakkala</option>
<option value="joensuu">Joensuu</option>
<option value="jokioinen">Jokioinen</option>
<option value="jomala">Jomala</option>
<option value="joroinen">Joroinen</option>
<option value="joutsa">Joutsa</option>
<option value="juankoski">Juankoski</option>
<option value="juuka">Juuka</option>
<option value="juupajoki">Juupajoki</option>
<option value="juva">Juva</option>
<option value="jyvaskyla">Jyv\xe4skyl\xe4</option>
<option value="jamijarvi">J\xe4mij\xe4rvi</option>
<option value="jamsa">J\xe4ms\xe4</option>
<option value="jarvenpaa">J\xe4rvenp\xe4\xe4</option>
<option value="kaarina">Kaarina</option>
<option value="kaavi">Kaavi</option>
<option value="kajaani">Kajaani</option>
<option value="kalajoki">Kalajoki</option>
<option value="kangasala">Kangasala</option>
<option value="kangasniemi">Kangasniemi</option>
<option value="kankaanpaa">Kankaanp\xe4\xe4</option>
<option value="kannonkoski">Kannonkoski</option>
<option value="kannus">Kannus</option>
<option value="karijoki">Karijoki</option>
<option value="karjalohja">Karjalohja</option>
<option value="karkkila">Karkkila</option>
<option value="karstula">Karstula</option>
<option value="karttula">Karttula</option>
<option value="karvia">Karvia</option>
<option value="kaskinen">Kaskinen</option>
<option value="kauhajoki">Kauhajoki</option>
<option value="kauhava">Kauhava</option>
<option value="kauniainen">Kauniainen</option>
<option value="kaustinen">Kaustinen</option>
<option value="keitele">Keitele</option>
<option value="kemi">Kemi</option>
<option value="kemijarvi">Kemij\xe4rvi</option>
<option value="keminmaa">Keminmaa</option>
<option value="kemionsaari">Kemi\xf6nsaari</option>
<option value="kempele">Kempele</option>
<option value="kerava">Kerava</option>
<option value="kerimaki">Kerim\xe4ki</option>
<option value="kesalahti">Kes\xe4lahti</option>
<option value="keuruu">Keuruu</option>
<option value="kihnio">Kihni\xf6</option>
<option value="kiikoinen">Kiikoinen</option>
<option value="kiiminki">Kiiminki</option>
<option value="kinnula">Kinnula</option>
<option value="kirkkonummi">Kirkkonummi</option>
<option value="kitee">Kitee</option>
<option value="kittila">Kittil\xe4</option>
<option value="kiuruvesi">Kiuruvesi</option>
<option value="kivijarvi">Kivij\xe4rvi</option>
<option value="kokemaki">Kokem\xe4ki</option>
<option value="kokkola">Kokkola</option>
<option value="kolari">Kolari</option>
<option value="konnevesi">Konnevesi</option>
<option value="kontiolahti">Kontiolahti</option>
<option value="korsnas">Korsn\xe4s</option>
<option value="koskitl">Koski Tl</option>
<option value="kotka">Kotka</option>
<option value="kouvola">Kouvola</option>
<option value="kristiinankaupunki">Kristiinankaupunki</option>
<option value="kruunupyy">Kruunupyy</option>
<option value="kuhmalahti">Kuhmalahti</option>
<option value="kuhmo">Kuhmo</option>
<option value="kuhmoinen">Kuhmoinen</option>
<option value="kumlinge">Kumlinge</option>
<option value="kuopio">Kuopio</option>
<option value="kuortane">Kuortane</option>
<option value="kurikka">Kurikka</option>
<option value="kustavi">Kustavi</option>
<option value="kuusamo">Kuusamo</option>
<option value="kylmakoski">Kylm\xe4koski</option>
<option value="kyyjarvi">Kyyj\xe4rvi</option>
<option value="karkola">K\xe4rk\xf6l\xe4</option>
<option value="karsamaki">K\xe4rs\xe4m\xe4ki</option>
<option value="kokar">K\xf6kar</option>
<option value="koylio">K\xf6yli\xf6</option>
<option value="lahti">Lahti</option>
<option value="laihia">Laihia</option>
<option value="laitila">Laitila</option>
<option value="lapinjarvi">Lapinj\xe4rvi</option>
<option value="lapinlahti">Lapinlahti</option>
<option value="lappajarvi">Lappaj\xe4rvi</option>
<option value="lappeenranta">Lappeenranta</option>
<option value="lapua">Lapua</option>
<option value="laukaa">Laukaa</option>
<option value="lavia">Lavia</option>
<option value="lemi">Lemi</option>
<option value="lemland">Lemland</option>
<option value="lempaala">Lemp\xe4\xe4l\xe4</option>
<option value="leppavirta">Lepp\xe4virta</option>
<option value="lestijarvi">Lestij\xe4rvi</option>
<option value="lieksa">Lieksa</option>
<option value="lieto">Lieto</option>
<option value="liminka">Liminka</option>
<option value="liperi">Liperi</option>
<option value="lohja">Lohja</option>
<option value="loimaa">Loimaa</option>
<option value="loppi">Loppi</option>
<option value="loviisa">Loviisa</option>
<option value="luhanka">Luhanka</option>
<option value="lumijoki">Lumijoki</option>
<option value="lumparland">Lumparland</option>
<option value="luoto">Luoto</option>
<option value="luumaki">Luum\xe4ki</option>
<option value="luvia">Luvia</option>
<option value="lansi-turunmaa">L\xe4nsi-Turunmaa</option>
<option value="maalahti">Maalahti</option>
<option value="maaninka">Maaninka</option>
<option value="maarianhamina">Maarianhamina</option>
<option value="marttila">Marttila</option>
<option value="masku">Masku</option>
<option value="merijarvi">Merij\xe4rvi</option>
<option value="merikarvia">Merikarvia</option>
<option value="miehikkala">Miehikk\xe4l\xe4</option>
<option value="mikkeli">Mikkeli</option>
<option value="muhos">Muhos</option>
<option value="multia">Multia</option>
<option value="muonio">Muonio</option>
<option value="mustasaari">Mustasaari</option>
<option value="muurame">Muurame</option>
<option value="mynamaki">Myn\xe4m\xe4ki</option>
<option value="myrskyla">Myrskyl\xe4</option>
<option value="mantsala">M\xe4nts\xe4l\xe4</option>
<option value="mantta-vilppula">M\xe4ntt\xe4-Vilppula</option>
<option value="mantyharju">M\xe4ntyharju</option>
<option value="naantali">Naantali</option>
<option value="nakkila">Nakkila</option>
<option value="nastola">Nastola</option>
<option value="nilsia">Nilsi\xe4</option>
<option value="nivala">Nivala</option>
<option value="nokia">Nokia</option>
<option value="nousiainen">Nousiainen</option>
<option value="nummi-pusula">Nummi-Pusula</option>
<option value="nurmes">Nurmes</option>
<option value="nurmijarvi">Nurmij\xe4rvi</option>
<option value="narpio">N\xe4rpi\xf6</option>
<option value="oravainen">Oravainen</option>
<option value="orimattila">Orimattila</option>
<option value="oripaa">Orip\xe4\xe4</option>
<option value="orivesi">Orivesi</option>
<option value="oulainen">Oulainen</option>
<option value="oulu">Oulu</option>
<option value="oulunsalo">Oulunsalo</option>
<option value="outokumpu">Outokumpu</option>
<option value="padasjoki">Padasjoki</option>
<option value="paimio">Paimio</option>
<option value="paltamo">Paltamo</option>
<option value="parikkala">Parikkala</option>
<option value="parkano">Parkano</option>
<option value="pedersore">Peders\xf6re</option>
<option value="pelkosenniemi">Pelkosenniemi</option>
<option value="pello">Pello</option>
<option value="perho">Perho</option>
<option value="pertunmaa">Pertunmaa</option>
<option value="petajavesi">Pet\xe4j\xe4vesi</option>
<option value="pieksamaki">Pieks\xe4m\xe4ki</option>
<option value="pielavesi">Pielavesi</option>
<option value="pietarsaari">Pietarsaari</option>
<option value="pihtipudas">Pihtipudas</option>
<option value="pirkkala">Pirkkala</option>
<option value="polvijarvi">Polvij\xe4rvi</option>
<option value="pomarkku">Pomarkku</option>
<option value="pori">Pori</option>
<option value="pornainen">Pornainen</option>
<option value="porvoo">Porvoo</option>
<option value="posio">Posio</option>
<option value="pudasjarvi">Pudasj\xe4rvi</option>
<option value="pukkila">Pukkila</option>
<option value="punkaharju">Punkaharju</option>
<option value="punkalaidun">Punkalaidun</option>
<option value="puolanka">Puolanka</option>
<option value="puumala">Puumala</option>
<option value="pyhtaa">Pyht\xe4\xe4</option>
<option value="pyhajoki">Pyh\xe4joki</option>
<option value="pyhajarvi">Pyh\xe4j\xe4rvi</option>
<option value="pyhanta">Pyh\xe4nt\xe4</option>
<option value="pyharanta">Pyh\xe4ranta</option>
<option value="palkane">P\xe4lk\xe4ne</option>
<option value="poytya">P\xf6yty\xe4</option>
<option value="raahe">Raahe</option>
<option value="raasepori">Raasepori</option>
<option value="raisio">Raisio</option>
<option value="rantasalmi">Rantasalmi</option>
<option value="ranua">Ranua</option>
<option value="rauma">Rauma</option>
<option value="rautalampi">Rautalampi</option>
<option value="rautavaara">Rautavaara</option>
<option value="rautjarvi">Rautj\xe4rvi</option>
<option value="reisjarvi">Reisj\xe4rvi</option>
<option value="riihimaki">Riihim\xe4ki</option>
<option value="ristiina">Ristiina</option>
<option value="ristijarvi">Ristij\xe4rvi</option>
<option value="rovaniemi">Rovaniemi</option>
<option value="ruokolahti">Ruokolahti</option>
<option value="ruovesi">Ruovesi</option>
<option value="rusko">Rusko</option>
<option value="raakkyla">R\xe4\xe4kkyl\xe4</option>
<option value="saarijarvi">Saarij\xe4rvi</option>
<option value="salla">Salla</option>
<option value="salo">Salo</option>
<option value="saltvik">Saltvik</option>
<option value="sastamala">Sastamala</option>
<option value="sauvo">Sauvo</option>
<option value="savitaipale">Savitaipale</option>
<option value="savonlinna">Savonlinna</option>
<option value="savukoski">Savukoski</option>
<option value="seinajoki">Sein\xe4joki</option>
<option value="sievi">Sievi</option>
<option value="siikainen">Siikainen</option>
<option value="siikajoki">Siikajoki</option>
<option value="siikalatva">Siikalatva</option>
<option value="siilinjarvi">Siilinj\xe4rvi</option>
<option value="simo">Simo</option>
<option value="sipoo">Sipoo</option>
<option value="siuntio">Siuntio</option>
<option value="sodankyla">Sodankyl\xe4</option>
<option value="soini">Soini</option>
<option value="somero">Somero</option>
<option value="sonkajarvi">Sonkaj\xe4rvi</option>
<option value="sotkamo">Sotkamo</option>
<option value="sottunga">Sottunga</option>
<option value="sulkava">Sulkava</option>
<option value="sund">Sund</option>
<option value="suomenniemi">Suomenniemi</option>
<option value="suomussalmi">Suomussalmi</option>
<option value="suonenjoki">Suonenjoki</option>
<option value="sysma">Sysm\xe4</option>
<option value="sakyla">S\xe4kyl\xe4</option>
<option value="taipalsaari">Taipalsaari</option>
<option value="taivalkoski">Taivalkoski</option>
<option value="taivassalo">Taivassalo</option>
<option value="tammela">Tammela</option>
<option value="tampere">Tampere</option>
<option value="tarvasjoki">Tarvasjoki</option>
<option value="tervo">Tervo</option>
<option value="tervola">Tervola</option>
<option value="teuva">Teuva</option>
<option value="tohmajarvi">Tohmaj\xe4rvi</option>
<option value="toholampi">Toholampi</option>
<option value="toivakka">Toivakka</option>
<option value="tornio">Tornio</option>
<option value="turku" selected="selected">Turku</option>
<option value="tuusniemi">Tuusniemi</option>
<option value="tuusula">Tuusula</option>
<option value="tyrnava">Tyrn\xe4v\xe4</option>
<option value="toysa">T\xf6ys\xe4</option>
<option value="ulvila">Ulvila</option>
<option value="urjala">Urjala</option>
<option value="utajarvi">Utaj\xe4rvi</option>
<option value="utsjoki">Utsjoki</option>
<option value="uurainen">Uurainen</option>
<option value="uusikaarlepyy">Uusikaarlepyy</option>
<option value="uusikaupunki">Uusikaupunki</option>
<option value="vaala">Vaala</option>
<option value="vaasa">Vaasa</option>
<option value="valkeakoski">Valkeakoski</option>
<option value="valtimo">Valtimo</option>
<option value="vantaa">Vantaa</option>
<option value="varkaus">Varkaus</option>
<option value="varpaisjarvi">Varpaisj\xe4rvi</option>
<option value="vehmaa">Vehmaa</option>
<option value="vesanto">Vesanto</option>
<option value="vesilahti">Vesilahti</option>
<option value="veteli">Veteli</option>
<option value="vierema">Vierem\xe4</option>
<option value="vihanti">Vihanti</option>
<option value="vihti">Vihti</option>
<option value="viitasaari">Viitasaari</option>
<option value="vimpeli">Vimpeli</option>
<option value="virolahti">Virolahti</option>
<option value="virrat">Virrat</option>
<option value="vardo">V\xe5rd\xf6</option>
<option value="vahakyro">V\xe4h\xe4kyr\xf6</option>
<option value="voyri-maksamaa">V\xf6yri-Maksamaa</option>
<option value="yli-ii">Yli-Ii</option>
<option value="ylitornio">Ylitornio</option>
<option value="ylivieska">Ylivieska</option>
<option value="ylojarvi">Yl\xf6j\xe4rvi</option>
<option value="ypaja">Yp\xe4j\xe4</option>
<option value="ahtari">\xc4ht\xe4ri</option>
<option value="aanekoski">\xc4\xe4nekoski</option>
</select>'


# FISocialSecurityNumber ##############################################################

>>> from django.contrib.localflavor.fi.forms import FISocialSecurityNumber
>>> f = FISocialSecurityNumber()
>>> f.clean('010101-0101')
u'010101-0101'
>>> f.clean('010101+0101')
u'010101+0101'
>>> f.clean('010101A0101')
u'010101A0101'
>>> f.clean('101010-0102')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid Finnish social security number.']
>>> f.clean('10a010-0101')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid Finnish social security number.']
>>> f.clean('101010-0\xe401')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid Finnish social security number.']
>>> f.clean('101010b0101')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid Finnish social security number.']
>>> f.clean('')
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']

>>> f.clean(None)
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']
>>> f = FISocialSecurityNumber(required=False)
>>> f.clean('010101-0101')
u'010101-0101'
>>> f.clean(None)
u''
>>> f.clean('')
u''
"""
