#
# A simple Evernote API demo script that lists all notebooks in the user's
# account and creates a simple test note in the default notebook.
#
# Before running this sample, you must fill in your Evernote developer token.
#
# To run (Unix):
#   export PYTHONPATH=../lib; python EDAMTest.py
#

import os
import sys
import time
import json

# Get file need to upload
fnote = open('/home/huangjian/.vnote', 'r').read()
print fnote
file_note = eval(fnote)
print file_note["title"]
#content = file_note["content"].replace("^@", "\n")
#content = file_note.replace("^@", '\n')

print file_note

