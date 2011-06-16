#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import sys
import os
import subprocess
from cue import CUE
from mutagen.flac import FLAC

def find_cues(root_dir):
    cues = list()
    cues.extend([os.path.join(root_dir, d) for d in os.listdir(root_dir) if d.lower().endswith('.cue') and not os.path.isdir(d)])
    subdirs = [os.path.join(root_dir, d) for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
    for subdir in subdirs:
        cues.extend(find_cues(subdir))
    return cues
        
def escape_string(string):
    return '%s' % (
        string
        .replace('\\', '\\\\')
        .replace(' ', '\\ ')
        .replace('(', '\(')
        .replace(')', '\)')
        .replace(',', '\,')
        .replace('"', '\"')
        .replace('$', '\$')
        .replace('&', '\&')
        .replace('!', '\!')
        .replace('`', '\`')
        .replace("'", "\\'")
    )

def get_image_file_name(cue):
    if os.path.exists(cue.image_file_name):
        return cue.image_file_name
    cuename = "".join(cue.file_name.split(".")[:-1]) + "."
    for name in [cuename + ext for ext in ["flac", "FLAC", "ape", "APE", "wv", "WV", "wav", "WAV"]]:
        if os.path.exists(name):
            return name
    return None

def main():
    # Getting CUE objects
    cues = [CUE(cue_file_name) for cue_file_name in find_cues(sys.argv[1]) if get_image_file_name(CUE(cue_file_name)) != None]
    if len(cues)==0:
        print("No CUE-sheets found. Sorry ._.")
        return
    # Showing list
    i = 1
    for cue in cues:
        print("#"+str(i)+" "+cue.file_name)
        print("  "+" "*len(str(i))),
        print(get_image_file_name(cue))
        i += 1
    raw_input("Press any key to start...")
    # Processing all images
    for cue in cues:
        if cue.image_file_name==None:
            print("ERROR: Image not found in "+cue.file_name)
            continue
        tmp_fname = cue.get_temporary_copy()
        ifn = get_image_file_name(cue)
        os.chdir(os.path.dirname(ifn))
        # Splitting image into files
        cmd = "shntool split "+escape_string(ifn)+" -f "+escape_string(tmp_fname)+" -o flac"
        print cmd
        return_code = 0
        return_code = subprocess.call(cmd, shell=1)
        # Stop process if splitting failed
        if return_code!=0:
            return
        if os.path.exists("split-track00.flac"):
            print("Removing split-track00.flac")
            os.remove("split-track00.flac")
        # Writing tags into splitted files & renaming them
        for track in cue.tracks:
            if not track.number==None:
                src_file_name = "split-track"+str(track.number).zfill(2)+".flac"
                dst_file_name = str(track.number).zfill(2)+' - '+track.title+'.flac'
                audio = FLAC(src_file_name)
                if not track.title==None:
                    audio["title"] = track.title
                #if not track.performer==None:
                #    audio["artist"] = track.performer
                #else:
                if cue.performer!=None:
                    audio["artist"] = cue.performer
                if not track.number==None:
                    audio["tracknumber"] = str(track.number)
                if not cue.title==None:
                    audio["album"] = cue.title
                if not track.isrc==None:
                    audio["isrc"] = track.isrc
                if not cue.genre==None:
                    audio["genre"] = cue.genre
                if not cue.date==None:
                    audio["date"] = cue.date
                if not cue.discid==None:
                    audio["discid"] = cue.discid
                if not cue.comment==None:
                    audio["comment"] = cue.comment
                # 0th track left blank
                audio["tracktotal"] = str(len(cue.tracks) - 1)
                audio.pprint()
                audio.save()
                os.chdir(os.path.dirname(ifn))
                os.rename(src_file_name, dst_file_name)  
        os.remove(tmp_fname)

if __name__ == '__main__':
    main()
