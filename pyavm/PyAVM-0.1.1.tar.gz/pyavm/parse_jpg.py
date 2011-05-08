f = open('2MASS_k_new.jpg')

markers = {}
markers['\xd8'] = 'SOI'
markers['\xc0'] = 'SOF0'
markers['\xc2'] = 'SOF2'
markers['\xc4'] = 'DHT'
markers['\xdb'] = 'DQT'
markers['\xdd'] = 'DRI'
markers['\xda'] = 'SOS'
markers['\xd0'] = 'RST0'
markers['\xd1'] = 'RST1'
markers['\xd2'] = 'RST2'
markers['\xd3'] = 'RST3'
markers['\xd4'] = 'RST4'
markers['\xd5'] = 'RST5'
markers['\xd6'] = 'RST6'
markers['\xd7'] = 'RST7'
markers['\xe0'] = 'APP0'
markers['\xe1'] = 'APP1'
markers['\xe2'] = 'APP2'
markers['\xe3'] = 'APP3'
markers['\xe4'] = 'APP4'
markers['\xe5'] = 'APP5'
markers['\xe6'] = 'APP6'
markers['\xe7'] = 'APP7'
markers['\xe8'] = 'APP8'
markers['\xe9'] = 'APP9'
markers['\xea'] = 'APP10'
markers['\xeb'] = 'APP11'
markers['\xec'] = 'APP12'
markers['\xed'] = 'APP13'
markers['\xee'] = 'APP14'
markers['\xef'] = 'APP15'
markers['\xfe'] = 'COM'
markers['\xd9'] = 'EOI'

c = 0
while True:
    c += 1
    m = f.read(1)
    if m == '':
        break
    if m == '\xff':
        m = f.read(1)
        if m in markers:
            print c, markers[m]
        # else:
            # print c, 'Unknown'
        