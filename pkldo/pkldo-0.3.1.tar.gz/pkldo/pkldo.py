#
# Filename: PKLDO.PY
#
# Copyright (C) 2009-2011 Andrew Pirus. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials
#    provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""Pickled Data Object"""

import cPickle
import struct
import errno
import time
import os
from binascii import crc32
from binascii import hexlify
from stat import *
from types import *

PDO_USE_LOCKING = False
PDO_USE_BSDLOCK = False

try:
    import fcntl
    PDO_USE_LOCKING = True
except ImportError:
    pass

try:
    getattr(os, 'O_SHLOCK')
    getattr(os, 'O_EXLOCK')
    PDO_USE_BSDLOCK = True
except AttributeError:
    pass

PDO_CURRENT_FORMAT_VERSION_MAJOR = 1
PDO_CURRENT_FORMAT_VERSION_MINOR = 0
PDO_CURRENT_PICKLE_VERSION = 1
PDO_FILE_SIGNATURE = "pkldo"
PDO_HEADER_FORMAT = ">5s3xHHHHII5s3xdQQII"
PDO_FILE_EXT_PDO = ".pdo"
PDO_FILE_EXT_ALT = ".alt"
PDO_FILE_EXT_NEW = ".new"
PDO_SIZE_STR = 1
PDO_SIZE_PAD = 1
PDO_SIZE_USHORT = 2
PDO_SIZE_UINT = 4
PDO_SIZE_FLOAT = 4
PDO_SIZE_DOUBLE = 8
PDO_SIZE_ULONGLONG = 8
PDO_UINT_MASK = 0xffffffff
PDO_DEFAULT_OBJTYPE = 0
PDO_DEFAULT_DOFLAGS = 0
PDO_EMPTY_VALUE = 0
PDO_HEADER_SIZE = 64
PDO_STATUS_SIZE = 5
PDO_STATUS_OFFSET = 24
PDO_STATUS_CLEAN = "clean"
PDO_STATUS_DIRTY = "dirty"
PDO_STATUS_TRASH = "trash"
PDO_H_SIG = 0
PDO_H_MAJ = 1
PDO_H_MIN = 2
PDO_H_OBJ = 3
PDO_H_PKL = 4
PDO_H_FLG = 5
PDO_H_RS1 = 6
PDO_H_STS = 7
PDO_H_TIM = 8
PDO_H_RS2 = 9
PDO_H_RS3 = 10
PDO_H_LEN = 11
PDO_H_CRC = 12
PDO_E_SIZE   = "bad file size"
PDO_E_SIG    = "bad file signature"
PDO_E_STATUS = "bad file status"
PDO_E_TIME   = "bad file time value"
PDO_E_RES    = "bad file reserved value"
PDO_E_DATA   = "bad file data type"
PDO_E_CRC    = "file crc error detected"
PDO_E_OBJ    = "file object type mismatch"
PDO_E_TRASH  = "file marked for deletion"
PDO_E_EXISTS = "file already exists"
PDO_E_FVER   = "unknown file version"
PDO_E_PVER   = "unknown pickle version"
PDO_E_PKL    = "error during pickle operation"
PDO_E_FAILED = "operation failed"

assert struct.calcsize(">s") == PDO_SIZE_STR
assert struct.calcsize(">x") == PDO_SIZE_PAD
assert struct.calcsize(">H") == PDO_SIZE_USHORT
assert struct.calcsize(">I") == PDO_SIZE_UINT
assert struct.calcsize(">f") == PDO_SIZE_FLOAT
assert struct.calcsize(">d") == PDO_SIZE_DOUBLE
assert struct.calcsize(">Q") == PDO_SIZE_ULONGLONG
assert struct.calcsize(PDO_HEADER_FORMAT) == PDO_HEADER_SIZE
assert len(PDO_STATUS_CLEAN) == PDO_STATUS_SIZE
assert len(PDO_STATUS_DIRTY) == PDO_STATUS_SIZE
assert len(PDO_STATUS_TRASH) == PDO_STATUS_SIZE

class PdoError(Exception):
    def __init__(self, err=None):
        self.err = err

    def __str__(self):
        if self.err is None:
            return ""
        if type(self.err) is StringType:
            return self.err
        return repr(self.err)

class PdoFileError(PdoError):
    def __init__(self, err=None):
        if err is None:
            self.err = "unknown file error"
        else:
            self.err = err

class PdoTrashError(PdoError):
    def __init__(self, err=None):
        if err is None:
            self.err = PDO_E_TRASH
        else:
            self.err = err

class PdoExistsError(PdoError):
    def __init__(self, err=None):
        if err is None:
            self.err = PDO_E_EXISTS
        else:
            self.err = err

class Pdo(object):
    def __init__(self):
        self.init_pdo()

    def init_pdo(self):
        """Initialize a PDO object.

        This must be called first before any PDO operations can be
        performed.  Either the PDO class constructor can be called,
        or the init_pdo method.  For example:

            Example 1
            ---------
            class Test1(Pdo):
                def __init__(self):
                    Pdo.__init__(self)
                    ...

            Example 2
            ---------
            class Test2(Pdo):
                def __init__(self):
                    self.init_pdo()
                    ...

            Example 3
            ---------
            class Test3(Pdo):
                def __init__(self):
                    pass

            test = Test3()
            test.init_pdo()
            ...

        """
        if not self.__beeninit():
            self._objtype    = PDO_DEFAULT_OBJTYPE
            self._flags      = PDO_DEFAULT_DOFLAGS
            self._filename   = None
            self._filetime   = 0
            self._filemask   = None
            self._filemode   = None
            self._recovered  = False
            self._loaderrors = None
            self._beeninit   = True
        else:
            raise PdoError, "PDO already initialized"

    def __beeninit(self):
        if hasattr(self, '_beeninit'):
            if self._beeninit is True:
                return True
        return False

    def __beenloaded(self):
        if not self.__beeninit():
            raise PdoError, "cannot check if loaded before initialized"
        if self._filename is None or self._filetime == 0:
            return False
        else:
            return True

    def set_objtype(self, objtype):
        self._objtype = objtype

    def set_flags(self, flags):
        self._flags = flags

    def __make_pdo_bytes(self, hd, pk):
        cs = crc32(hd[:-PDO_SIZE_UINT] + pk) & PDO_UINT_MASK
        hd = hd[:-PDO_SIZE_UINT] + struct.pack(">I", cs)
        hd = hd[:PDO_STATUS_OFFSET] + PDO_STATUS_DIRTY + hd[PDO_STATUS_OFFSET + PDO_STATUS_SIZE:]
        return hd + pk

    def __open_file_shlock(self, file, flags, mode=0777):
        if PDO_USE_BSDLOCK:
            flags |= os.O_SHLOCK
        fd = os.open(file, flags, mode)
        if PDO_USE_LOCKING and not PDO_USE_BSDLOCK:
            try:
                fcntl.flock(fd, fcntl.LOCK_SH)
            except: 
                raise OSError
        return fd

    def __open_file_exlock(self, file, flags, mode=0777):
        if PDO_USE_BSDLOCK:
            flags |= os.O_EXLOCK
        fd = os.open(file, flags, mode)
        if PDO_USE_LOCKING and not PDO_USE_BSDLOCK:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
            except:
                raise OSError
        return fd

    def __read_pdo_file(self, fobj):
        try:
            bytes = fobj.read()
            filesize = len(bytes)
            if filesize < PDO_HEADER_SIZE:
                raise PdoFileError(PDO_E_SIZE)
            hd = bytes[:PDO_HEADER_SIZE]
            hdinfo = struct.unpack(PDO_HEADER_FORMAT, hd)
            if hdinfo[PDO_H_SIG] != PDO_FILE_SIGNATURE:
                raise PdoFileError(PDO_E_SIG)
            if hdinfo[PDO_H_STS] != PDO_STATUS_CLEAN:
                if hdinfo[PDO_H_STS] == PDO_STATUS_DIRTY:
                    raise PdoFileError(PDO_E_STATUS)
                elif hdinfo[PDO_H_STS] == PDO_STATUS_TRASH:
                    raise PdoTrashError
                else:
                    raise PdoFileError(PDO_E_STATUS)
            if hdinfo[PDO_H_TIM] == 0:
                raise PdoFileError(PDO_E_TIME)
            if filesize != (PDO_HEADER_SIZE + hdinfo[PDO_H_LEN]):
                raise PdoFileError(PDO_E_SIZE)
            pk = bytes[PDO_HEADER_SIZE:]
            if hdinfo[PDO_H_CRC] != crc32(hd[:-PDO_SIZE_UINT] + pk) & PDO_UINT_MASK:
                raise PdoFileError(PDO_E_CRC)
            if hdinfo[PDO_H_OBJ] != self._objtype:
                raise PdoFileError(PDO_E_OBJ)
            if hdinfo[PDO_H_MAJ] == 1 and hdinfo[PDO_H_MIN] == 0:
                if hdinfo[PDO_H_RS1] != PDO_EMPTY_VALUE:
                    raise PdoFileError(PDO_E_RES)
                if hdinfo[PDO_H_RS2] != PDO_EMPTY_VALUE:
                   raise PdoFileError(PDO_E_RES)
                if hdinfo[PDO_H_RS3] != PDO_EMPTY_VALUE:
                   raise PdoFileError(PDO_E_RES)
                #
                # check hdinfo[PDO_H_FLG] here...    
                #
            else:
                raise PdoFileError(PDO_E_FVER)
            if hdinfo[PDO_H_PKL] not in range(3):
                raise PdoFileError(PDO_E_PVER)
            try:
                pkdata = cPickle.loads(pk)
            except:
                raise PdoError(PDO_E_PKL)
            if type(pkdata) is not DictType:
                raise PdoFileError(PDO_E_DATA)
            for key, value in pkdata.items():
                if key[0] == '_' or type(value) is MethodType:
                    raise PdoFileError(PDO_E_DATA)
        except PdoError:
            raise
        except:
            raise PdoError(PDO_E_FAILED)
        return (hdinfo, pkdata)

    def __write_clean(self, fobj, s):
        fobj.write(s)
        fobj.seek(PDO_STATUS_OFFSET, os.SEEK_SET)
        fobj.write(PDO_STATUS_CLEAN)

    def __write_clean_truncate(self, fobj, s):
        fobj.write(s)
        fobj.truncate()
        fobj.seek(PDO_STATUS_OFFSET, os.SEEK_SET)
        fobj.write(PDO_STATUS_CLEAN)

    def __write_trash(self, fobj):
        fobj.seek(PDO_STATUS_OFFSET, os.SEEK_SET)
        fobj.write(PDO_STATUS_TRASH)

    def create_pdo(self, filename, filemask=None, filemode=None):
        """Creates new backing files for a PDO.

        Specify the full file name without any extension.  The
        appropriate file extensions are added automatically.  If
        the file name already exists, this method will fail.  This
        is because a PDO should be treated like a primary key in
        a database.  Once the key is created, it does not change.
        This is a somewhat basic way to keep PDO name integrity.

        Two files will be created.  The first is the main copy with
        ".pdo" as the default file extension.  The second is the
        alternate copy with ".alt" as the default extension.  Both
        copies are used for making file operations atomic and to
        provide built-in redundancy.  Both files are identical to
        help prevent minor disk/file corruption.

        A different file mask (umask) and/or file mode (chmod) can be
        specified.  Otherwise, the process file mask is used in
        combination with the default file mode of "0777".  These
        values should be specified in octal if used as an argument.
        Always do a test run to check the permissions that the files
        end up with.  Do not assume since this can be easily confused.

        If you specify a custom file mask or file mode, be sure to use
        the same values when calling save_pdo.  Otherwise, file
        permissions may not stay consistent.

        An error will be generated if create_pdo is called before the
        PDO is initialized.  Also, create_pdo will generate an error
        if either create_pdo or load_pdo have already been called.

        """
        if not self.__beeninit():
            raise PdoError, "must call init_pdo before calling create_pdo"
        if self.__beenloaded():
            raise PdoError, "PDO already created or loaded"
        if type(filename) is not StringType:
            raise TypeError, "filename argument should be a string"
        if filemask is None:
            filemask = os.umask(0)
            os.umask(filemask)
        if type(filemask) is not IntType:
            raise TypeError, "filemask argument should be an integer in octal notation"
        if filemode is None:
            filemode = 0777
        if type(filemode) is not IntType:
            raise TypeError, "filemode argument should be an integer in octal notation"
        fdpdo = -1
        fdalt = -1
        fppdo = None
        fpalt = None
        fnpdo = filename + PDO_FILE_EXT_PDO
        fnalt = filename + PDO_FILE_EXT_ALT
        fnnew = filename + PDO_FILE_EXT_NEW
        oldmask = os.umask(filemask)
        try:
            # always open the pdo file first to do the locking
            fdpdo = self.__open_file_exlock(fnpdo,
                        os.O_RDWR | os.O_CREAT | os.O_EXCL,
                        filemode)
        except OSError, e:
            if e.errno == errno.EEXIST:
                raise PdoExistsError
            else:
                raise PdoError(PDO_E_FAILED)
        finally:
            os.umask(oldmask)
        oldmask = os.umask(filemask)
        try:
            fdalt = self.__open_file_exlock(fnalt,
                        os.O_RDWR | os.O_CREAT | os.O_EXCL,
                        filemode)
        except OSError, e:
            if e.errno == errno.EEXIST:
                raise PdoExistsError
            else:
                raise PdoError(PDO_E_FAILED)
        finally:
            if fdalt == -1:
                os.unlink(fnpdo)
            os.umask(oldmask)
        if os.path.exists(fnnew):
            # delete in reverse order
            os.unlink(fnalt)
            os.unlink(fnpdo)
            raise PdoExistsError
        data = {}
        for key, value in self.__dict__.items():
            if key[0] == '_' or type(value) is MethodType:
                continue
            data[key] = value
        try:
            pkdata = cPickle.dumps(data, PDO_CURRENT_PICKLE_VERSION)
        except:
            # delete in reverse order
            os.unlink(fnalt)
            os.unlink(fnpdo)
            raise PdoError(PDO_E_PKL)
        try:
            A_signature  = PDO_FILE_SIGNATURE
            B_ver_major  = PDO_CURRENT_FORMAT_VERSION_MAJOR
            C_ver_minor  = PDO_CURRENT_FORMAT_VERSION_MINOR
            D_objtype    = self._objtype
            E_pkl_ver    = PDO_CURRENT_PICKLE_VERSION
            F_flags      = self._flags
            G_reserved_1 = PDO_EMPTY_VALUE
            H_status     = PDO_STATUS_CLEAN
            I_timestamp  = time.time()
            if I_timestamp == 0:
                raise PdoError, "cannot use time value of zero"
            J_reserved_2 = PDO_EMPTY_VALUE
            K_reserved_3 = PDO_EMPTY_VALUE
            L_length     = len(pkdata)
            M_checksum   = PDO_EMPTY_VALUE
            header = struct.pack(PDO_HEADER_FORMAT, \
                                 A_signature, \
                                 B_ver_major, \
                                 C_ver_minor, \
                                 D_objtype, \
                                 E_pkl_ver, \
                                 F_flags, \
                                 G_reserved_1, \
                                 H_status, \
                                 I_timestamp, \
                                 J_reserved_2, \
                                 K_reserved_3, \
                                 L_length, \
                                 M_checksum)
            bytes = self.__make_pdo_bytes(header, pkdata)
            fppdo = os.fdopen(fdpdo, 'w+b')
            fpalt = os.fdopen(fdalt, 'w+b')
            self.__write_clean(fppdo, bytes)
            self.__write_clean(fpalt, bytes)
            fppdo.flush()
            fpalt.flush()
            os.fsync(fppdo.fileno())
            os.fsync(fpalt.fileno())
            fpalt.close()
            # keep the pdo file open until the very end to maintain the lock
            fppdo.close()
        except:
            # delete in reverse order
            os.unlink(fnalt)
            os.unlink(fnpdo)
            raise PdoError(PDO_E_FAILED)
        self._filename = filename
        self._filetime = I_timestamp
        self._filemask = filemask
        self._filemode = filemode

    def save_pdo(self, filemask=None, filemode=None):
        """Saves changes made to a PDO.

        The files backing a PDO are updated to reflect any recent
        modifications to the actual PDO object.  This operation
        will try to be atomic by first creating a temporary copy
        with the ".new" file extension.  If successful, the main
        copy is updated, followed by the alternate copy.  If any
        failures occur during this process, there should always
        be a copy that can be recovered when it is next loaded.

        Depending on the requirements, a file mask (umask) and file
        mode (chmod) can be specified.  There are 3 situations that
        will be tried in order by save_pdo to pick the settings:

            1. Use filemask and/or filemode arguments

                If a custom file mask or file mode is specified,
                the values will take first priority and be used.
                Basically, if a custom file mask or file mode was
                used with create_pdo, use it with save_pdo.  This
                should keep file permissions consistent.  This is
                a workaround to fill gaps in the way PDO files are
                handled.  It's better left to the application to
                determine what settings it needs.

                If file permissions need to be changed, it should
                not be done via the call to save_pdo.  This will
                be likely to result in file permission problems.
                Instead, change the file permissions using operating
                system calls and update your application to start
                using the new values.

            2. Use values remembered from previous calls

                A PDO object will remember the file mask and file
                mode values used on previous calls to create_pdo
                and save_pdo.  Therefore, you do not need to specify
                them on subsequent calls to save_pdo.  However, it
                would be considered a better approach to always
                specify the values you want.

            3. Use the default values for the process

                Default values will be used if no other option has
                been specified or is available.  The process mask
                is used for the file mask and the value "0777" is
                used for the file mode.  This option is best if
                nothing was originally specified in prior calls to
                create_pdo or save_pdo.

        Does not take filename argument since a PDO can only be saved
        following a call to create_pdo or load_pdo.  The filename is
        remembered so that only the original PDO is modified.  An
        error will be generated if save_pdo is called before the PDO
        is initialized.  Also, save_pdo will generate an error if
        either create_pdo or load_pdo have not yet been called.

        """
        if not self.__beeninit():
            raise PdoError, "must call init_pdo before calling save_pdo"
        if not self.__beenloaded():
            raise PdoError, "save_pdo cannot be called prior to create_pdo or load_pdo"
        #
        # choose filemask and filemode in this order: argument, current, or default
        #
        if filemask is not None:
            pass
        elif self._filemask is not None:
            filemask = self._filemask
        else:
            filemask = os.umask(0)
            os.umask(filemask)
        if type(filemask) is not IntType:
            raise TypeError, "filemask argument should be an integer in octal notation"
        if filemode is not None:
            pass
        elif self._filemode is not None:
            filemode = self._filemode
        else:
            filemode = 0777
        if type(filemode) is not IntType:
            raise TypeError, "filemode argument should be an integer in octal notation"
        fdpdo = -1
        fdnew = -1
        fppdo = None
        fpnew = None
        fnpdo = self._filename + PDO_FILE_EXT_PDO
        fnnew = self._filename + PDO_FILE_EXT_NEW
        fnalt = self._filename + PDO_FILE_EXT_ALT
        try:
            # always open the pdo file first to do the locking
            fdpdo = self.__open_file_exlock(fnpdo, os.O_RDWR)
        except:
            raise PdoError(PDO_E_FAILED)
        oldmask = os.umask(filemask)
        try:
            fdnew = self.__open_file_exlock(fnnew,
                        os.O_RDWR | os.O_CREAT | os.O_TRUNC,
                        filemode)
        except:
            raise PdoError(PDO_E_FAILED)
        finally:
            os.umask(oldmask)
        data = {}
        for key, value in self.__dict__.items():
            if key[0] == '_' or type(value) is MethodType:
                continue
            data[key] = value
        try:
            pkdata = cPickle.dumps(data, PDO_CURRENT_PICKLE_VERSION)
        except:
            os.unlink(fnnew)
            raise PdoError(PDO_E_PKL)
        try:
            A_signature  = PDO_FILE_SIGNATURE
            B_ver_major  = PDO_CURRENT_FORMAT_VERSION_MAJOR
            C_ver_minor  = PDO_CURRENT_FORMAT_VERSION_MINOR
            D_objtype    = self._objtype
            E_pkl_ver    = PDO_CURRENT_PICKLE_VERSION
            F_flags      = self._flags
            G_reserved_1 = PDO_EMPTY_VALUE
            H_status     = PDO_STATUS_CLEAN
            I_timestamp  = time.time()
            if I_timestamp == 0:
                raise PdoError, "cannot use time value of zero"
            J_reserved_2 = PDO_EMPTY_VALUE
            K_reserved_3 = PDO_EMPTY_VALUE
            L_length     = len(pkdata)
            M_checksum   = PDO_EMPTY_VALUE
            header = struct.pack(PDO_HEADER_FORMAT, \
                                 A_signature, \
                                 B_ver_major, \
                                 C_ver_minor, \
                                 D_objtype, \
                                 E_pkl_ver, \
                                 F_flags, \
                                 G_reserved_1, \
                                 H_status, \
                                 I_timestamp, \
                                 J_reserved_2, \
                                 K_reserved_3, \
                                 L_length, \
                                 M_checksum)
            bytes = self.__make_pdo_bytes(header, pkdata)
            fpnew = os.fdopen(fdnew, 'w+b')
            self.__write_clean(fpnew, bytes)
            fpnew.flush()
            os.fsync(fpnew.fileno())
        except:
            os.unlink(fnnew)
            raise PdoError(PDO_E_FAILED)
        try:
            fppdo = os.fdopen(fdpdo, 'w+b')
            self.__write_clean_truncate(fppdo, bytes)
            fppdo.flush()
            os.fsync(fppdo.fileno())
        except:
            raise PdoError(PDO_E_FAILED)
        try:
            os.rename(fnnew, fnalt)
        except:
            raise PdoError(PDO_E_FAILED)
        finally:
            fpnew.close()
            # keep the pdo file open until the very end to maintain the lock
            fppdo.close()
        self._filetime = I_timestamp
        self._filemask = filemask
        self._filemode = filemode

    def load_pdo(self, filename):
        """Loads a PDO from its backing files.

        Specify the full file name without any extension.  Each of
        the possible file extensions are checked.  If any problem
        is detected, the best copy will be used.  However, no
        corrections will be made to the underlying files since
        this is a read-only operation.  If no good copies can be
        found, then an error will be generated.

        An error will be generated if load_pdo is called before the
        PDO is initialized.  Also, load_pdo will generate an error
        if either create_pdo or load_pdo have already been called.

        """
        #
        # TODO: document how to check if file recovery took place
        #       and what can be done about it
        #
        if not self.__beeninit():
            raise PdoError, "must call init_pdo before calling load_pdo"
        if self.__beenloaded():
            raise PdoError, "PDO already created or loaded"
        if type(filename) is not StringType:
            raise TypeError, "filename argument should be a string"
        fdpdo = -1
        fdnew = -1
        fdalt = -1
        fppdo = None
        fpnew = None
        fpalt = None
        fnpdo = filename + PDO_FILE_EXT_PDO
        fnnew = filename + PDO_FILE_EXT_NEW
        fnalt = filename + PDO_FILE_EXT_ALT
        pdo_loaded = False
        new_loaded = False
        alt_loaded = False
        good_hdinfo = None
        good_pkdata = None
        pdo_err_msg = None
        new_err_msg = None
        alt_err_msg = None
        self._loaderrors = None
        try:
            try:
                # always open the pdo file first to do the locking
                fdpdo = self.__open_file_shlock(fnpdo, os.O_RDONLY)
            except:
                pdo_err_msg = PDO_E_FAILED
                raise
            try:
                fppdo = os.fdopen(fdpdo, 'rb')
                (pdo_hdinfo, pdo_pkdata) = self.__read_pdo_file(fppdo)
                pdo_loaded = True
            except PdoTrashError:
                pdo_err_msg = PDO_E_TRASH
                raise
            except PdoError, e:
                pdo_err_msg = str(e)
            except:
                pdo_err_msg = PDO_E_FAILED
            if os.path.exists(fnnew):
                try:
                    fdnew = self.__open_file_shlock(fnnew, os.O_RDONLY)
                    fpnew = os.fdopen(fdnew, 'rb')
                    (new_hdinfo, new_pkdata) = self.__read_pdo_file(fpnew)
                    new_loaded = True
                except PdoError, e:
                    new_err_msg = str(e)
                except:
                    new_err_msg = PDO_E_FAILED
            if pdo_loaded:
                if new_loaded:
                    if new_hdinfo[PDO_H_TIM] > pdo_hdinfo[PDO_H_TIM]:
                        good_hdinfo = new_hdinfo
                        good_pkdata = new_pkdata
                    else:
                        good_hdinfo = pdo_hdinfo
                        good_pkdata = pdo_pkdata
                else:
                    good_hdinfo = pdo_hdinfo
                    good_pkdata = pdo_pkdata
            elif new_loaded:
                good_hdinfo = new_hdinfo
                good_pkdata = new_pkdata
            else:
                try:
                    fdalt = self.__open_file_shlock(fnalt, os.O_RDONLY)
                    fpalt = os.fdopen(fdalt, 'rb')
                    (alt_hdinfo, alt_pkdata) = self.__read_pdo_file(fpalt)
                    alt_loaded = True
                    good_hdinfo = alt_hdinfo
                    good_pkdata = alt_pkdata
                except PdoError, e:
                    alt_err_msg = str(e)
                    raise
                except:
                    alt_err_msg = PDO_E_FAILED
                    raise
            if not good_hdinfo or not good_pkdata:
                raise PdoError(PDO_E_FAILED)
            self.__dict__.update(good_pkdata)
            self._filename = filename
            self._filetime = good_hdinfo[PDO_H_TIM]
            if new_loaded or alt_loaded:
                self._recovered = True
        except PdoError:
            raise
        except:
            raise PdoError(PDO_E_FAILED)
        finally:
            self._loaderrors = (pdo_err_msg, new_err_msg, alt_err_msg)

    def delete_pdo(self):
        """Deletes the files backing a PDO.

        Does not take filename argument so this method cannot be
        abused to delete files from any path.  Therefore, a PDO must
        already have been created or loaded before it can be deleted.

        Tries to be atomic by marking the PDO as trash before actually
        deleting any files on disk.  If marking the PDO as trash fails,
        then the alternate file can still be used to recover the PDO.

        Also, files will not be deleted if the main ".pdo" copy does
        not exist or cannot be accessed.  This behavior is included to
        maintain file locking and access order.  If the file must be
        force deleted, then system calls or os commands can be used.

        An error will be generated if delete_pdo is called before the
        PDO is initialized.  Also, delete_pdo will generate an error
        if either create_pdo or load_pdo have not yet been called.

        """
        if not self.__beeninit():
            raise PdoError, "must call init_pdo before calling delete_pdo"
        if not self.__beenloaded():
            raise PdoError, "delete_pdo cannot be called prior to create_pdo or load_pdo"
        fdpdo = -1
        fdnew = -1
        fdalt = -1
        fppdo = None
        fnpdo = self._filename + PDO_FILE_EXT_PDO
        fnnew = self._filename + PDO_FILE_EXT_NEW
        fnalt = self._filename + PDO_FILE_EXT_ALT
        try:
            # always open the pdo file first to do the locking
            fdpdo = self.__open_file_exlock(fnpdo, os.O_RDWR)
            fppdo = os.fdopen(fdpdo, 'w+b')
            self.__write_trash(fppdo)
            fppdo.flush()
            os.fsync(fppdo.fileno())
            if os.path.exists(fnnew):
                fdnew = self.__open_file_exlock(fnnew, os.O_RDWR)
            if os.path.exists(fnalt):
                fdalt = self.__open_file_exlock(fnalt, os.O_RDWR)
            if fdalt != -1:
                os.unlink(fnalt)
                os.close(fdalt)
            if fdnew != -1:
                os.unlink(fnnew)
                os.close(fdnew)
            os.unlink(fnpdo)
            # keep the pdo file open until the very end to maintain the lock
            fppdo.close()
        except:
            raise PdoError(PDO_E_FAILED)


#
# EOF
#
