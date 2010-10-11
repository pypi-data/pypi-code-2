from Image import fromstring
from qr_encode import encode as _qrencode
from qr_decode import decode as _qrdecode

encoding_dict={'QR_MODE_NUM':0,'QR_MODE_AN':1,'QR_MODE_8':2,'QR_MODE_KANJI':3}
## //0: Numeric mode //1: Alphabet-numeric mode //2: 8-bit Data mode //3: Kanji (shift-jis) mode
error_correction_dict={'QR_ECLEVEL_L':0,'QR_ECLEVEL_M':1,'QR_ECLEVEL_Q':2,'QR_ECLEVEL_H':3}
## Low to high error correction level
default_image_width=400 #pixel
default_case_sensitiveness=True
default_version=5
default_error_correction='QR_ECLEVEL_L'
default_encoding='QR_MODE_AN'

max_len_case_sensitive = 102
max_len_case_insensitive = 190

def encode(string, image_width=default_image_width,case_sensitive=default_case_sensitiveness,version=default_version,error_correction_level=default_error_correction,encoding_hint=default_encoding):
    """Returns a PIL image of the QR code generated from the given string"""
    #try a few times to encode due to some weired problem with returned data sometimes being shorter
    if case_sensitive:
        case_sensitive = 1
    else:
        case_sensitive = 0
    if error_correction_dict.has_key(error_correction_level):
        error_correction_level=error_correction_dict[error_correction_level]
    else:
        print 'Unknown specified error correction level. Using default error correction level',default_error_correction
        error_correction_level=error_correction_dict[default_error_correction]
    if encoding_dict.has_key(encoding_hint):
        encoding_hint=encoding_dict[encoding_hint]
    else:
        print 'Unknown specified encoding hint. Using default encoding',default_encoding
        encoding_hint=encoding_dict[default_encoding]
    version = int(version)
    if ((version > 10) or (version <0)):
        print 'Specified QR version is not allowed (0 <= version <= 10). Using default version:',default_version
    if ((case_sensitive) and (len(string) > max_len_case_sensitive)):
        print 'Warning: string is too long ('+str(len(string))+'), it will probably not be readable (max lenght of case sensitive string is '+str(max_len_case_sensitive)+')'
    if ((not case_sensitive) and (len(string) > max_len_case_insensitive)):
        print 'Warning: string is too long ('+str(len(string))+'), it will probably not be readable (max lenght of case insensitive string is '+str(max_len_case_insensitive)+')'

    version, width, data = _qrencode(string+'\0',case_sensitive,version,error_correction_level,encoding_hint)
    dot_size = image_width / width
    actual_width = width * (dot_size)
    raw_data = ''
    for y in range(width):
        line = ''
        for x in range(width):
            if ord(data[y*width+x])%2:
                line += dot_size*chr(0)
            else:
                line += dot_size*chr(255)
        lines = dot_size*line
        raw_data += lines

    #print 'Lenght of raw data string: ',len(raw_data)
    #print 'Image size: ',actual_width, actual_width*actual_width
    image = fromstring('L',(actual_width,actual_width),raw_data)
    return (width,image)

def decode(image_file):
    """Decode QR image and return data string. QR must be an image file."""
    status,string = _qrdecode(image_file)
    ret_status = False
    comment = ''
    if _getBitValue(status,14):
        comment+='QR_IMAGEREADER_ERROR: '
        if _getBitValue(status,8): comment+='QR_IMAGEREADER_NOT_INVALID_SRC_IMAGE, '
        if _getBitValue(status,9): comment+='QR_IMAGEREADER_NOT_FOUND_FINDER_PATTERN, '
        if _getBitValue(status,10): comment+='QR_IMAGEREADER_NOT_FOUND_CODE_AREA, '
        if _getBitValue(status,11): comment+='QR_IMAGEREADER_NOT_DETERMINABLE_CODE_AREA, '
    else:
        if _getBitValue(status,12): comment+='QR_IMAGEREADER_WORKING, '
        if _getBitValue(status,13): comment+='QR_IMAGEREADER_DECODED, '; ret_status=True
        if _getBitValue(status,8): comment+='QR_VERSIONINFO_INVALID, '
        if _getBitValue(status,9): comment+='QR_VERSIONINFO_MISMATCH, '
        if _getBitValue(status,11): comment+='QR_VERSIONINFO_UNRECOVERABLE, '
        if _getBitValue(status,4): comment+='QR_FORMATINFO_INVALID_LEVE, '
        if _getBitValue(status,7): comment+='QR_FORMATINFO_UNRECOVERABLE, '
        if _getBitValue(status,0): comment+='QR_CODEDATA_NOT_SUPPORT_ECI, '
        if _getBitValue(status,1): comment+='QR_CODEDATA_LENGTH_MISMATCH, '
        if _getBitValue(status,3): comment+='QR_CODEDATA_UNRECOVERABLE, '

    if comment == '':
        comment = 'Unknown return status'
    print comment
    return (ret_status,string)



def _Denary2Binary(n):
    '''convert denary (base 10) integer n to binary string bStr'''
    bStr = ''
    if n < 0: raise ValueError, "must be a positive"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr

def _getBitValue(n, p):
    '''get the bitvalue of denary (base 10) number n at the equivalent binary position p (binary count starts at position 0 from the right)'''
    return (n >> p) & 1

def listEncoderEncodings():
    """List possible values for encoding_hint parameter of function encode()"""
    return encoding_dict.keys()

def listEncoderErrorLevels():
    """List possible values for error_correction_level parameter of function encode()"""
    return error_correction_dict.keys()

def printEncoderDefaults():
    """Prints default values for parameters of function encode()"""
    print 'image_width             : ',default_image_width
    print 'case_sensitive          : ',default_case_sensitiveness
    print 'version                 : ',default_version
    print 'error_correction_level  : ',default_error_correction
    print 'encoding_hint           : ',default_encoding




def demo():
    import sys
    print 'QR Codec demo'
    try:
        text = sys.argv[1]
    except:
        text = 'blabla'
    filename = 'test.png'
    print 'Encoding some text: ',text
    width,image = encode(text,image_width=600,version=5,error_correction_level='QR_ECLEVEL_L',case_sensitive=False)
    print 'QR code created, saving image..'
    try:
        image.save(filename)
        print 'Image saved'
    except:
        print 'It was not possible to save the image, make sure you have write permissions.'
        return False
    print 'Decoding QR code..'
    status,string = decode(filename)
    if status == True:
        print 'Image decoded: ',string
    print 'End'


if __name__ == '__main__':
    demo()