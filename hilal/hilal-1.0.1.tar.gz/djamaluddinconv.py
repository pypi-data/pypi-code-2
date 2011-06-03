#-------------------------------------------------------------------------------
# Name:        djamaluddinconv.py
# Purpose: Adopting Hijri-Gregorian Calendar Converter courtesy of
# Thomas Djamaluddin.
#
# Author:      Anung
#
# Created:     17/05/2011
# Copyright:   (c) Anung 2011
# Licence:     <your licence>
# 20110521 hijriMonthName(), solarMonthName()
# 20110520 Separate solarToHijri() to solarToHijriMenu(), to make it callable and usable for other modules. The same applies to hijriToSolar().
# 20110516 Start.
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    print "*** Calendar Conversion Program ***"
    print " Hijri (Islamic Calendar) <-> Solar Calendar "
    print " (Caution: There is the Islamic Date Line which"
    print " causes this calculation may differ about (+/-) 1 day)."
    print " 6 August 1991, 25 Muharram 1412"
    print " Calculated by T.Djamaluddin"
    print " Dept. of Astronomy, Kyoto University"
    print " Sakyo-Ku, Kyoto 606, Japan"
    print "*******"
    print ""
    conv = ""
    while conv <> 0:
        print "1. Conversion Hijri (Islamic Calendar) to Solar Calendar"
        print "2. Conversion Solar Calendar to Hijri (Islamic Calendar)"
        print ""
        conv = input("Choose 1 or 2 (0 to exit):")
        if (conv == 1):
            hijriToSolarMenu()
        elif (conv == 2):
            solarToHijriMenu()
        else:
            pass


def hijriToSolarMenu():
    '''
    Ask user to enter (assume valid) Hijri date. Calls
    hijriToSolar().
    '''
    print "*** Conversion from Hijri to Solar Calendar ***"
    print ""
    hd = input("Hijri date:")
    print "1. Muharram      5. Jumadil Awal    9. Ramadhan"
    print "2. Safar         6. Jumadil Akhir  10. Syawal"
    print "3. Rabiul Awal   7. Rajab          11. Zulqaidah"
    print "4. Rabiul Akhir  8. Shaban         12. Zulhijjah"
    hm = input("Hijri month:")
    hy = input("Hijri year:")
    (sd, sm, sy) = hijriToSolar(hd, hm, hy)
    print hd, hm, hy, "Hijri is", sd, sm, sy, "A.D."


def hijriToSolar(hd, hm, hy):
    '''
    Converts a given Hijri date to Solar date.
    '''
    nhd1 = (hy - 1) * 354.3671 + (hm - 1) * 29.5306 + hd
    nhd = int(nhd1)
    nsd = nhd1 + 227016
    if nhd > 350721:
        gc = 10
    else:
        gc = 0
    if nhd > 393898:
        gc = 11
    if nhd > 430422:
        gc = 12
    if nhd > 466946:
        gc = 13
    sy = int( (nsd + gc)/365.25) + 1
    mn = round((nsd+gc)-(sy-1)*365.25)
    #350 MN  = CINT((NSD+GC)-(SY-1)*365.25)
    mn1 = 0
    sm = 1
    if mn > 31:
        mn1 = 31
        sm = 2
    if int(sy/4) == (sy/4):
        (mn1, sm) = gosub700(mn)
    else:
        (mn1, sm) = gosub580(mn)
    if sy == 1700 or sy == 1800:
        (mn1, sm) = gosub580(mn)
    if sy == 1900:
        (mn1, sm) = gosub580(mn)

    smStr = solarMonthName(sm)

    sd = mn - mn1
    return (sd, sm, sy)
    #GOTO 110


def solarMonthName(sm):
    '''
    Given a month number 'sm', returns its corresponding solar month name.
    '''

    # Result
    if sm == 1:
        smStr = " January "
    if sm == 2:
        smStr = " February "
    if sm == 3:
        smStr = " March "
    if sm == 4:
        smStr = " April "
    if sm == 5:
        smStr = " May "
    if sm == 6:
        smStr = " June "
    if sm == 7:
        smStr = " July "
    if sm == 8:
        smStr = " August "
    if sm == 9:
        smStr = " September "
    if sm == 10:
        smStr = " October "
    if sm == 11:
        smStr = " November "
    if sm == 12:
        smStr = " December "

    return smStr


def gosub700(mn):
    # Leap (Kabisat) Year
    if mn > 60:
        mn1 = 60
        sm = 3
    if mn > 91:
        mn1 = 91
        sm = 4
    if mn > 121:
        mn1 = 121
        sm = 5
    if mn > 152:
        mn1 = 152
        sm = 6
    if mn > 182:
        mn1 = 182
        sm = 7
    if mn > 213:
        mn1 = 213
        sm = 8
    if mn > 244:
        mn1 = 244
        sm = 9
    if mn > 274:
        mn1 = 274
        sm = 10
    if mn > 335:
        mn1 = 305
        sm = 11
    if mn > 335:
        mn1 = 335
        sm = 12

    return (mn1, sm)


def gosub580(mn):
    # Ordinary (Basitah) Year
    if mn > 59:
        mn1 = 59
        sm = 3
    if mn > 90:
        mn1 = 90
        sm = 4
    if mn > 120:
        mn1 = 120
        sm = 5
    if mn > 151:
        mn1 = 151
        sm = 6
    if mn > 181:
        mn1 = 181
        sm = 7
    if mn > 212:
        mn1 = 212
        sm = 8
    if mn > 243:
        mn1 = 243
        sm = 9
    if mn > 273:
        mn1 = 273
        sm = 10
    if mn > 304:
        mn1 = 304
        sm = 11
    if mn > 334:
        mn1 = 334
        sm = 12

    return (mn1, sm)


def solarToHijriMenu():
    '''
    Ask user to enter (assume valid) Gregorian date. Calls
    solarToHijri().
    '''
    print "*** Solar Calendar to Hijri ***"
    sd = input("Solar date:")
    print "1. January   5. May      9. September"
    print "2. February  6. June    10. October"
    print "3. March     7. July    11. November"
    print "4. April     8. August  12. December"
    sm = input("Solar month:")
    sy = input("Solar year:")
    (hd, hm, hy) = solarToHijri(sd, sm, sy)
    print sd, sm, sy, "A.D. is", hd, hm, hy, "Hijri (", ddStr, ")"


def solarToHijri(sd, sm, sy):
    '''
    Calculates a Hijri date to Solar date.
    '''
    if sm == 1:
        mn = 0
    if sm == 2:
        mn = 31
    if sm == 3:
        mn = 59
    if sm == 4:
        mn = 90
    if sm == 5:
        mn = 120
    if sm == 6:
        mn = 151
    if sm == 7:
        mn = 181
    if sm == 8:
        mn = 212
    if sm == 9:
        mn = 243
    if sm == 10:
        mn = 273
    if sm == 11:
        mn = 304
    if sm == 12:
        mn = 334

    y = sy + (mn + sd)/ 365.25
    if y > 1582.76 and y < 1582.788:
        #1060 IF Y>1582.76 AND Y<1582.788 THEN PRINT ?GREGORIAN : OMITTED?: GOTO 110
        print "Gregorian: Omitted"
        return None
    else:
        if y > 1582.76:
            gc = 10
        else:
            gc = 0
        if y > 1701:
            gc = 11
        if y > 1801:
            gc = 12
        if y > 1901:
            gc = 13
        ydn = (sy - 1) * 365.25
        if sm < 3:
            # goto 1160
            pass
        else:
            if int(sy/4) == (sy/4):
                mn = mn + 1
            if sy == 1700:
                mn = mn - 1
            if sy == 1800 or sy == 1900:
                mn = mn - 1
        nsd = ydn + mn + sd - gc
        nhd1 = nsd - 227016
        nhd = int(nhd1)
        hy = int(nhd1/354.3671 + 1)
        hm1 = round(nhd1 - (hy - 1) * 354.3671)
        #1190 HM1 = CINT(NHD1 ? (HY-1)*354.3671)
        hm = int(hm1/29.5306) + 1
        hd = round(hm1 - (hm - 1) * 29.5306)
        #1210 HD  = CINT(HM1 ? (HM-1)*29.5306 ) : GOSUB 1400
        ddStr = gosub1400(nhd)
        if hd == 0:
            hm = hm - 1
            hd = 30

        hmStr = hijriMonthName(hm)

        # Result
        if hm == 0:
            hmStr = " Zulhijjah "
            hy = hy - 1
        if hm == 1:
            hmStr = " Muharram "
        if hm == 2:
            hmStr = " Safar "
        if hm == 3:
            hmStr = " Rabiul Awal "
        if hm == 4:
            hmStr = " Rabiul Akhir "
        if hm == 5:
            hmStr = " Jumadil Awal "
        if hm == 6:
            hmStr = " Jumadil Akhir "
        if hm == 7:
            hmStr = " Rajab "
        if hm == 8:
            hmStr = " Shaban "
        if hm == 9:
            hmStr = " Ramadhan "
        if hm == 10:
            hmStr = " Shawal "
        if hm == 11:
            hmStr = " Zulqaidah "
        if hm == 12:
            hmStr = " Zulhijjah "

        return (hd, hm, hy)


def hijriMonthName(hm):
    '''
    Given a Hijri month number 'hm', returns corresponding Hijri month name.
    '''

    # Result
    if hm == 0:
        hmStr = " Zulhijjah "
        hy = hy - 1
    if hm == 1:
        hmStr = " Muharram "
    if hm == 2:
        hmStr = " Safar "
    if hm == 3:
        hmStr = " Rabiul Awal "
    if hm == 4:
        hmStr = " Rabiul Akhir "
    if hm == 5:
        hmStr = " Jumadil Awal "
    if hm == 6:
        hmStr = " Jumadil Akhir "
    if hm == 7:
        hmStr = " Rajab "
    if hm == 8:
        hmStr = " Shaban "
    if hm == 9:
        hmStr = " Ramadhan "
    if hm == 10:
        hmStr = " Shawal "
    if hm == 11:
        hmStr = " Zulqaidah "
    if hm == 12:
        hmStr = " Zulhijjah "

    return hmStr


def gosub1400(nhd):
    # The day
    nhd1 = nhd - 7 * int(nhd/7)
    dd = nhd1 % 7
    if dd == 0:
        ddStr = " Thursday "
    if dd == 1:
        ddStr = " Friday "
    if dd == 2:
        ddStr = " Saturday "
    if dd == 3:
        ddStr = " Sunday "
    if dd == 4:
        ddStr = " Monday "
    if dd == 5:
        ddStr = " Tuesday "
    if dd == 6:
        ddStr = " Wednesday "

    return ddStr


if __name__ == '__main__':
    main()
