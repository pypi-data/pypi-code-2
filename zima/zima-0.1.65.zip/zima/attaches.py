# -*- coding: utf-8 -*-
import os
import StringIO

import mimetypes
import Image, ImageFile

from names import uid, fpath, uqpath
from errors import AttachDuplicationError, ForbiddenAttachTypeError, \
    InvalidAttachError, StorageCollisionError

def image_handler(cfg, file):
    parser = ImageFile.Parser()
    parser.feed(file['data'])
    img = parser.close()
    file['size'] = [len(file['data']), list(img.size)]
    thumb = img.copy()
    thumb.thumbnail(cfg.thumbs.size, cfg.thumbs.useAA \
        and Image.ANTIALIAS or Image.NEAREST)
    output = StringIO.StringIO()
    thumb.save(output, cfg.thumbs.format)
    file['thumb']= {
            'size': list(thumb.size),
            'name': [file['name'][0]+'s', '.'+cfg.thumbs.format.lower()],
            'data': output.getvalue(),
            'type': 'image'}

def default_handler(cfg, file):
    file['size'] = (len(file['data']),)
    
attach_handlers = {
    'application/octet-stream': default_handler,
    'default': default_handler,
    'image/x-png': image_handler,            
    'image/png': image_handler,
    'image/jpeg': image_handler,
    'image/pjpeg': image_handler,
    'image/gif': image_handler
}

def add_attach(cfg, relid, file, chksums, hook):
   if 'hash' not in file:
       from binascii import crc32
       file['hash'] = crc32(file['data'])
   if 'mime' not in file:
       file['mime'] = mimetypes.guess_type(''.join(file['name']))[0]
   if 'name' not in file or cfg.forceRename:
        ext = mimetypes.guess_extension(file['mime']) or ''
        file['name'] = [uid(), ext]
   file['name'] = [uqpath(file['name'][0], cfg.pathFs, file['name'][1]), file['name'][1]]
   if 'meta' not in file:
       meta = file.get('meta', {})
       meta['relid'] = relid
       meta['name'] = file['name']
   if cfg.requireUnique:
      try:
          chksums.reg_attach(file['hash'], meta)
      except StorageCollisionError, e: 
          raise AttachDuplicationError(e)
   try:
       attach_handlers[file['mime']](cfg, file)
   except KeyError:
       attach_handlers['default'](cfg, file)
   file = hook('newAttach', file)
   open(fpath(cfg.pathFs, *file['name']), 'wb').write(file['data'])
   del file['data']
   if 'thumb' in file and file['thumb'] <> None:
       thumb = file['thumb']
       open(fpath(cfg.thumbs.pathFs, *thumb['name']), 'wb').write(thumb['data'])
       del thumb['data']
   return file

def del_attach(cfg, file, chksums):
    os.remove(fpath(cfg.pathFs, *file['name']))
    if 'thumb' in file:
        os.remove(fpath(cfg.thumbs.pathFs, *file['thumb']['name']))
    if cfg.requireUnique:
        chksums.del_attach({'name': file['name']})
        
