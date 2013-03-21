from PyQt4.QtCore import QObject, pyqtSignal, QTimer
import nemebean.mythnimal.libvlc as libvlc
from Settings import settings
import time

class VLC(QObject):
   fileFinished = pyqtSignal()
   playbackStarted = pyqtSignal()
   foundAspect = pyqtSignal()
   foundVolume = pyqtSignal(int)
   foundPosition = pyqtSignal()

   def __init__(self, label, filename, extraOptions = ''):
      super(VLC, self).__init__()
      
      self.outputLabel = label
      self.filename = filename
      self.deinterlace = True
      
      self.clear()
      
      self._vlc = libvlc.MediaPlayer(filename)
      self._vlc.set_xwindow(self.outputLabel.winId())
      self._vlc.video_set_scale(0)
      self._vlc.video_set_deinterlace('linear')
      self._vlc.play()
      
      self.timer = QTimer()
      self.timer.setInterval(100)
      self.timer.timeout.connect(self.update)
      self.timer.start()
      
      self.lengthTimer = QTimer()
      self.lengthTimer.setInterval(settings['lengthUpdateInterval'])
      self.lengthTimer.timeout.connect(self.updateLength)
      self.lengthTimer.start()
      
   
   def end(self):
      self._vlc.stop()
      self.timer.stop()
      self.lengthTimer.stop()
      
      
   def clear(self):
      self.length = 0
      self.position = 0
      self.fps = 0
      self.playing = True
      self.width = 0
      self.height = 0
      
      
   def update(self):
      # Means the file ended
      if not self._vlc.will_play():
         self.fileFinished.emit()
      
      self.position = self._vlc.get_time() / 1000
      self.foundPosition.emit()
      
      oldWidth = self.width
      oldHeight = self.height
      (self.width, self.height) = self._vlc.video_get_size()
      
      if oldWidth != self.width or oldHeight != self.height:
         self.aspect = self._vlc.video_get_aspect_ratio()
         if self.aspect is None:
            self.aspect = float(self.width) / float(self.height)
         print self.aspect
         self.foundAspect.emit()
      
      self.fps = self._vlc.get_fps()
      if self.fps < .01:
         self.fps = 60
         
         
   def updateLength(self):
      instance = self._vlc.get_instance()
      media = instance.media_new(self.filename)
      media.parse()
      self.length = 0
      start = time.time()
      while self.length <= 0:
         # In case we can't get the length for some reason
         if time.time() - start > 1:
            self.length = self.position
            print 'Failed to get time'
            break
         self.length = media.get_duration() / 1000
         print media.get_duration()
      print self.length
      
      
   def play(self):
      self._vlc.pause()
      self.playing = not self.playing
      
      
   def seekRelative(self, amount):
      self._vlc.set_time(int(self.position + amount) * 1000)
      
      
   def toggleDeinterlacing(self):
      self.deinterlace = not self.deinterlace
      