import Queue
import threading
import os, tempfile
import transaction

from tg import config

media_worker = Queue.Queue()
generate_thumb_cmd = "ffmpeg -y -i '%s' -intra -s 200x150 -ss 0:0:5.0 -vframes 1  -vcodec png  -y -f image2 '%s'"
worker_thread = None

class MediaWorkerThread(threading.Thread):
      
      convert_video_ogg_cmd = "ffmpeg2theora '%s' -x 480 -y 368 --optimize -o '%s'"
      convert_video_mov_cmd = "ffmpeg -y -i '%s' -acodec libfaac -s 480x368 -vcodec libx264 -vpre normal -vb 600k -r 20 -g 30 -ab 128k '%s'"

      def run(self):
          print 'Media Worker thread is running.'

          while True:
           msg = media_worker.get()
           try:
              print 'Converting video'

              video_file = msg['video']
              upload_dir = os.path.join(msg['public_dir'], 'rdisk', 'video')

              if not os.path.isdir(upload_dir):
                 os.mkdir(upload_dir)

              video_path = 'rdisk/video/video_' + msg['name']

              ogg_video_file_path = os.path.join(msg['public_dir'], video_path + '.ogg')
              os.system(MediaWorkerThread.convert_video_ogg_cmd % (video_file, ogg_video_file_path))

              mov_video_file_path = os.path.join(msg['public_dir'], video_path + '.mov')
              os.system(MediaWorkerThread.convert_video_mov_cmd % (video_file, mov_video_file_path))

              transaction.commit()
              print 'Done Conversion'

           except Exception, e:
              print 'Unable to process in worker thread: ' + str(e)
              media_worker.task_done()


def start_media_worker():
    global worker_thread
    worker_thread = MediaWorkerThread()
    worker_thread.start()

def convert_video(public_dir, name, video):
    if not worker_thread:
        start_media_worker()

    media_worker.put({'public_dir':public_dir,
                      'name':name,'video': video})

