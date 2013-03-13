#!/usr/bin/env python

from dulwich import repo

import envoy
import subprocess
import os
import shutil
import filecmp

shutil.rmtree('.screencaptures', True)
os.mkdir('.screencaptures')

git = repo.Repo('.')
history = git.revision_history(git.head())

history.reverse()

last_filename = None

for i, commit in enumerate(history):
    sha = commit.id
    timestamp = commit.commit_time
    filename = '.screencaptures/%s.jpg' % timestamp
    print "%i Checking out commit %s" % (i, sha)
    envoy.run('git checkout %s' % sha)
    r = envoy.run('phantomjs etc/screencapture.js %s' % filename)
    print r.std_out
    print r.std_err
    if not os.path.exists(filename):
        print 'WARNING: Image not generated by Phantom.'
        continue

    if last_filename and filecmp.cmp(last_filename, filename, False):
        print 'Removing duplicate image %s' % filename
        os.remove(filename)

    else:
        if filecmp.cmp(filename, 'etc/darkness.jpg', False):
            print 'Removing darkness.'
            os.remove(filename)

        else:
            last_filename = filename

shutil.copyfile(last_filename, '.screencapture/0.jpg')

proc = subprocess.Popen(['ffmpeg', '-f', 'image2', '-r', '2', '-qscale', '2', '-pattern_type', 'glob', '-i', '*.jpg', 'video.mp4'], cwd='.screencaptures')
proc.wait()
