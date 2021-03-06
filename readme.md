### Big Scary Disclaimer ###
While Mythnimal mostly just reads from your Myth environment, it does make a few changes as well.  I am not responsible if it completely trashes your installation, nor for any other negative consequences of using this application.

### (Mostly) Less Scary Stuff ###
Now, with that out of the way I'll give a quick overview of Mythnimal.  It was born out of my frustration with the official Mythfrontend, in particular the lack of any sort of backward or forward compatibility.  At some point I realized that I only used a tiny fraction of the functionality of Mythfrontend, and that functionality would be fairly easy to implement in a new frontend.

As of this writing, Mythnimal implements most of the features I use on a regular basis.  Things it can do include watching previously recorded shows and watching live tv.  At this point it only officially supports the protocol used in Myth .24 and .25, but in theory it could handle more than that without anything more than trivial changes.

If you're feeling adventurous and want to try using a frontend that is still under fairly heavy development, there are a few things you need to know:

1. It needs access to both your Myth database and your Myth recordings directory.  This frontend _cannot_ stream from the Myth backend at this time, so it needs direct access to the files.  You will be prompted at the first run to provide the necessary paths/information.
2. Keybindings are largely the same as regular Myth, except that space is pause and the program guide is g.
3. This frontend uses MPlayer to play recordings, so you will need that installed, along with Python, Qt4, PyQt4, and SQLAlchemy.
4. Mythnimal is also capable of using MPlayer2 as a video player, and I actually recommend using that instead because it seems to work better with HD content.  You can change the video player by altering the MPlayer command in the settings screen.
5. Another reminder: This is in very early development right now, so the code is going to be in flux for a while.  What gets checked in to the Git repo _probably_ works for me, but no guarantees.

Assuming all goes well with this project, at some point I will probably write something up on the GitHub wiki for it.  Until then, this is all the documentation you're getting. ;-)