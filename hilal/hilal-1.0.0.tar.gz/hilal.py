#-------------------------------------------------------------------------------
# Name:        hilal.py
# Purpose:     Calculates hilal (first-crescent) visibility using
# pyEphem package.
#
# Author:      Anung Ariwibowo, barliant@gmail.com
#
# Created:     17/05/2011
# Copyright:   (c) Anung 2011
# Licence:     <your licence>
# version:
# 20110520 Memanfaatkan program konversi tanggal Thomas Djamaluddin
#  Next: Passing parameter pyEphem's Observer object.
#  Next: Koreksi ketinggian bulan 34 menit (atau derajat?) Check
#  dokumentasi pyEphem.
# 20110518 TODO: Parameter dengan objek Observer
# 20110517 Mulai. Salin-tempel fungsi kalender dari shalat.py
#   FIX: Memetakan nama bulan Hijriah. Metonic cycle? Konversi
#   tanggal Thomas Djamaluddin.
#-------------------------------------------------------------------------------
#!/usr/bin/env python

'''
hilal.py
Calculates hilal (first-crescent) visibility using pyEphem package.
Anung Ariwibowo, barliant@gmail.com
20110517, 14320611
'''

import ephem
import datetime
import djamaluddinconv


# Beberapa tetapan (konstanta)
# Separasi elongasi Bulan - Matahari (3 derajat)
sepLimit = ephem.degrees('03:00:00')
# Tinggi Bulan di atas ufuk (2 derajat)
altLimit = ephem.degrees('02:00:00')
# Umur Hilal (8 jam)
ageLimit = ephem.Date(8 * ephem.hour)
epZero = ephem.Date(0)
epHalfDay = ephem.Date(epZero + (12*ephem.hour))
epFullDay = ephem.Date(epZero + (24*ephem.hour))


# SET TO False to suppress Debug information
DBG = True


def main():
    #jkt19960122()
    #jkt19960220()
    #idulAdha1431()
    #ramadhan1432()
    #syawal1432()
    #zulhijjah1432()

# Jakarta
    jakartaHariIni()
# Singapore
    #sgHariIni()
# Mekah
    mekahHariIni()



def hijriDate(lokasi, waktu=ephem.now(), monthName=False):
    '''
    Returns Hijri date (in string format of the form HY/HM/HD) for
    a given location 'lokasi' and date-time 'waktu'. Default
    date-time is ephem.now(). If 'monthName' is True, returns the
    name of the Hijri month instead of Hijri month number.
    '''
    firstDay = kalender(lokasi, waktu)
    currentDay = ephem.Date(waktu)
    (hd, hm, hy) = djamaluddinconv.solarToHijri(currentDay.tuple()[2], currentDay.tuple()[1], currentDay.tuple()[0])
    hdStr = djamaluddinconv.hijriMonthName(hm)
    hd = int(currentDay-firstDay)+1
    if monthName:
        strResult = str(hd)+" "+hdStr+" "+str(hy)
    else:
        strResult = str(hy)+"/"+str(int(hm))+"/"+str(hd)

    if DBG:
        print "DBG: hijriDate(): currentDay:", currentDay
        print "DBG: hijriDate():   firstDay:", firstDay

    return strResult


def kalender(lokasi, waktu=ephem.now()):
    '''
    Given location 'lokasi' and date-time 'waktu', calculates
    visibility of the next hilal and the next-next hilal. Default
    for 'waktu' is ephem.now()
    '''
#    loc = ephem.city(lokasi)
    loc = lokasi
    loc.date = waktu

    # set tanggal lokasi ke bulan baru terakhir sebelum 'waktu'.
    newMoon = ephem.previous_new_moon(loc.date)
    loc.date = newMoon

# Objek Bulan dan Matahari
    bulan = ephem.Moon(loc)
    matahari = ephem.Sun(loc)

    waktuSekarang = ephem.now()
    delta = ephem.Date(0)
    umurHilal = ephem.Date(0)
    sep = ephem.degrees('0:0:0')

    #while (umurHilal < epFullDay) and (sep <= sepLimit):
    while not ( (umurHilal > ageLimit) or (bulan.alt > altLimit and sep > sepLimit) ):
    #while (umurHilal <= ageLimit) and ( ( bulan.alt <= altLimit or sep <= sepLimit) ):
        # informasi terbenam bulan dan matahari setelah bulan baru terakhir
        moonSet = loc.next_setting(bulan)
        sunSet = loc.next_setting(matahari)
        umurHilal = ephem.Date(sunSet-newMoon)

        if moonSet > sunSet:
            loc.date = moonSet
            delta = ephem.Date(moonSet-sunSet)
        else:
            loc.date = sunSet
            delta = ephem.Date(sunSet - moonSet)

        sep = ephem.separation((matahari.az, matahari.alt), \
                (bulan.az, bulan.alt))

        if DBG:
            print "\tPosisi matahari (az, alt): (",matahari.az,",",matahari.alt,")"
            print "\tPosisi bulan    (az, alt): (",bulan.az,",",bulan.alt,")"
            print "\tSeparasi Bulan-Matahari:", sep
            print "\tWaktu Konjungsi:", ephem.localtime(newMoon)
            print "\tUmur hilal:", dateDiff(umurHilal)
            print "\tBulan terbenam", dateDiff(delta), "setelah matahari."

    tanggalSatu = sunSet
    if DBG:
        print "Tanggal 1 Hijriah:", tanggalSatu, "UTC", \
            "atau", ephem.localtime(tanggalSatu), "di", loc.name
        print "Posisi matahari (az, alt): (",matahari.az,",",matahari.alt,")"
        print "Posisi bulan    (az, alt): (",bulan.az,",",bulan.alt,")"
        print "Separasi Bulan-Matahari:", sep
        print "Waktu Konjungsi:", ephem.localtime(newMoon)
        print "Umur hilal:", dateDiff(umurHilal)
        print "Bulan terbenam", dateDiff(delta), "setelah matahari."

    nextNewMoon = ephem.next_new_moon(tanggalSatu)
    loc.date = nextNewMoon

    delta = ephem.Date(0)
    umurHilal = ephem.Date(0)
    sep = ephem.degrees('00:00:00')

    #while (umurHilal < epFullDay) and (sep <= sepLimit):
    while not ( (umurHilal > ageLimit) or (bulan.alt > altLimit and sep > sepLimit) ):
        moonSet = loc.next_setting(bulan)
        sunSet = loc.next_setting(matahari)
        umurHilal = ephem.Date(sunSet-nextNewMoon)

        if moonSet > sunSet:
            loc.date = moonSet
            delta = ephem.Date(moonSet-sunSet)
        else:
            loc.date = sunSet
            delta = ephem.Date(sunSet-moonSet)

        sep = ephem.separation((matahari.az, matahari.alt), \
                (bulan.az, bulan.alt))

        if DBG:
            print "\tPosisi matahari (az, alt): (",matahari.az,",",matahari.alt,")"
            print "\tPosisi bulan    (az, alt): (",bulan.az,",",bulan.alt,")"
            print "\tSeparasi Bulan-Matahari:", sep
            print "\tWaktu Konjungsi:", ephem.localtime(nextNewMoon)
            print "\tUmur hilal:", dateDiff(umurHilal)
            print "\tBulan terbenam", dateDiff(delta), "setelah matahari."

    tanggalSatuBerikut = sunSet
    umurBulan = ephem.Date(tanggalSatuBerikut - tanggalSatu)
    if DBG:
        print "Tanggal 1 Hijriah bulan berikutnya:", \
            tanggalSatuBerikut, "UTC atau", \
            ephem.localtime(tanggalSatuBerikut), "di", loc.name
        print "Posisi matahari (az, alt): (",matahari.az,", \
            ",matahari.alt,")"
        print "Posisi   bulan  (az, alt): (",bulan.az,", \
            ",bulan.alt,")"
        print "Separasi Bulan-Matahari:", sep
        print "Umur hilal:", dateDiff(umurHilal)
        print "Bulan terbenam", dateDiff(delta), "setelah matahari."
        print "Umur bulan kalender", umurBulan.tuple()[2], "hari."

    return tanggalSatu


def jkt19960122():
    print "=== Jakarta, 22 Januari 1996 ==="
    kalender(ephem.city('Jakarta'), ephem.Date('1996/01/22 00:00:00'))
    print ""


def jkt19960220():
    print "=== Jakarta, 20 Februari 1996 ==="
    kalender(ephem.city('Jakarta'), ephem.Date('1996/02/20 00:00:00'))
    print ""


def idulAdha1431():
    # Idul Adha 1431
    print "== Idul Adha 1431, Jakarta =="
    kalender(ephem.city('Jakarta'), ephem.Date('2010/11/07 00:00:00'))
    print ""


def ramadhan1432():
    # Ramadhan 1432
    print "=== Ramadhan 1432, Jakarta ==="
    (dd, mm, yy) = djamaluddinconv.hijriToSolar(1, 9, 1432)
    strDate = str(yy)+"/"+str(mm)+"/"+str(dd)
    #kalender(ephem.city('Jakarta'), ephem.Date('2011/07/31'))
    kalender(ephem.city('Jakarta'), ephem.Date(strDate))


def syawal1432():
    # Syawal 1432
    print "=== Syawal 1432, Jakarta ==="
    (dd, mm, yy) = djamaluddinconv.hijriToSolar(1, 10, 1432)
    strDate = str(yy)+"/"+str(mm)+"/"+str(dd)
    #kalender(ephem.city('Jakarta'), ephem.Date('2011/08/30'))
    kalender(ephem.city('Jakarta'), ephem.Date(strDate))
    print ""

def zulhijjah1432():
    print "=== Zulhijjah 1432, Jakarta ==="
    (dd, mm, yy) = djamaluddinconv.hijriToSolar(1, 12, 1432)
    strDate = str(yy)+"/"+str(mm)+"/"+str(dd)
    #kalender(ephem.city('Jakarta'), ephem.Date('2011/08/30'))
    kalender(ephem.city('Jakarta'), ephem.Date(strDate))
    print ""


def jakartaHariIni():
    print "== Jakarta, hari ini =="
    tglSatu = kalender(ephem.city('Jakarta'))
    print "Tanggal 1 Hijriah:", tglSatu, ephem.localtime(tglSatu)
    tglSekarang = ephem.Date(ephem.now())
    (hm, hd, hy) = djamaluddinconv.solarToHijri(tglSekarang.tuple()[2], \
        tglSekarang.tuple()[1], tglSekarang.tuple()[0])
    hdStr = djamaluddinconv.hijriMonthName(hd)
    print "Hari ini tanggal", int(tglSekarang-tglSatu)+1, hdStr, hy, "H."
    print "Hari ini tanggal", tglSekarang, "M."


def sgHariIni():
    print "== Singapore, hari ini =="
    tglSatu = kalender(ephem.city('Singapore'))
    print "Tanggal 1 Hijriah:", tglSatu, ephem.localtime(tglSatu)
    tglSekarang = ephem.Date(ephem.now())
    (hm, hd, hy) = djamaluddinconv.solarToHijri(tglSekarang.tuple()[2], \
        tglSekarang.tuple()[1], tglSekarang.tuple()[0])
    hdStr = djamaluddinconv.hijriMonthName(hd)
    print "Hari ini tanggal", int(tglSekarang-tglSatu)+1, hdStr, hy, "H."
    print "Hari ini tanggal", tglSekarang, "M."


def mekahHariIni():
    mekah = ephem.Observer()
    mekah.lon = '39.8262'
    mekah.lat = '21.4227'
    mekah.elevation = 277
    mekah.compute_pressure()
    mekah.name = "Mekah"

    tglSatu = kalender(mekah)
    tglSekarang = ephem.Date(ephem.now())
    (hm, hd, hy) = djamaluddinconv.solarToHijri(tglSekarang.tuple()[2], \
        tglSekarang.tuple()[1], tglSekarang.tuple()[0])
    hdStr = djamaluddinconv.hijriMonthName(hd)

    print "== Mekkah, hari ini =="
    print "Tanggal 1 Hijriah:", tglSatu, ephem.localtime(tglSatu)
    print "Hari ini tanggal", int(tglSekarang-tglSatu)+1, hdStr, hy, "H."
    print "Hari ini tanggal", tglSekarang, "M."


def dateDiff(tanggal, acuan=ephem.Date(0)):
    '''
    Given a date 'tanggal' (in ephem.Date format), returns a
    string. Assume difference between 'tanggal' and 'acuan' is not
    more than a month away.
    '''
    selisih = datetime.timedelta(tanggal, acuan)
    strKalimat = str(selisih)
    strKalimat = strKalimat.replace("day,", "hari")
    strKalimat = strKalimat.replace("days", "hari")
    return strKalimat


if __name__ == '__main__':
    main()
