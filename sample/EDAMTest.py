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
os.sys.path.append("../lib")
import hashlib
import binascii
import time
import json
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

def get_resource(attach):
    '''
    To display the Resource as part of the note's content, 
    include an <en-media> tag in the note's ENML content. 
    The en-media tag identifies the corresponding
    Resource using the MD5 hash.
    '''             
    md5 = hashlib.md5()
    md5.update(attach)
    hash = md5.digest()
    hashHex = binascii.hexlify(hash)

    '''
    To include an attachment such as an image in a note, 
    first create a Resource for the attachment. 
    At a minimum, the Resource contains the binary attachment data, 
    an MD5 hash of the binary data, and the attachment MIME type. 
    It can also include attributes such as filename and location.
    '''
    data = Types.Data()
    data.size = len(attach)
    data.bodyHash = hash
    data.body = attach

    resource = Types.Resource()
    resource.mime = 'image/png'
    resource.data = data
    return resource, hashHex 
     
def get_authtoken():
    '''
    Real applications authenticate with Evernote using OAuth, but for the
    purpose of exploring the API, you can get a developer token that allows
    you to access your own Evernote account. To get a developer token, visit 
    https://sandbox.evernote.com/api/DeveloperToken.action
    '''
    if len(sys.argv) < 2:
        authToken = "S=s1:U=3b225:E=14241270f3f:C=13ae975e343:P=1cd:A=en-devtoken:H=c6b548c4216c28f3f2bc54d4496a0100"
    else:
        authToken = sys.argv[1]

    if authToken == "your developer token":
        print "Please fill in your developer token"
        print "To get a developer token, visit https://sandbox.evernote.com/api/DeveloperToken.action"
        exit(1)
    return authToken

if __name__ == "__main__":
    authToken = get_authtoken()
    '''
    Initial development is performed on our sandbox server. 
    To use the production service, 
    change "sandbox.evernote.com" to "www.evernote.com" and replace your
    developer token above with a token from 
    https://www.evernote.com/api/DeveloperToken.action
    '''
    evernoteHost = "sandbox.evernote.com"
    userStoreUri = "https://" + evernoteHost + "/edam/user"

    userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
    userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
    userStore = UserStore.Client(userStoreProtocol)

    versionOK = userStore.checkVersion("Evernote EDAMTest (Python)",
                                    UserStoreConstants.EDAM_VERSION_MAJOR,
                                    UserStoreConstants.EDAM_VERSION_MINOR)
    print "Is my Evernote API version up to date? ", str(versionOK)
    print ""
    if not versionOK:
        exit(1)

    '''
    Get the URL used to interact with the contents of the user's account
    When your application authenticates using OAuth, the NoteStore URL will
    be returned along with the auth token in the final OAuth request.
    In that case, you don't need to make this call.
    '''

    noteStoreUrl = userStore.getNoteStoreUrl(authToken)

    noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
    noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
    noteStore = NoteStore.Client(noteStoreProtocol)

    # List all of the notebooks in the user's account        
    notebooks = noteStore.listNotebooks(authToken)
    print "Found ", len(notebooks), " notebooks:"
    for notebook in notebooks:
        print "  * ", notebook.name

    print
    print "Creating a new note in the default notebook"
    print
    
    # Get file need to upload
    vnote = {}
    vnote = eval(open('/home/huangjian/.vnote', 'r').read())  

    '''
    To create a new note, simply create a new Note object and fill in 
    attributes such as the note's title.
    '''
    note = Types.Note()
    note.title = vnote["title"]

    if (vnote.has_key("attachment")) and (len(vnote["attachment"]) > 0):
        (resource, hashHex) = get_resource(vnote["attachment"])
        note.resources = [ resource ]

    '''
    The content of an Evernote note is represented 
    using Evernote Markup Language (ENML). 
    The full ENML specification can be found in the Evernote API Overview
    at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    '''
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    note.content += '<en-note>' + vnote["content"] + '<br/>'
    if vnote.has_key("attachment"):
        note.content += '<en-media type="image/png" hash="' + hashHex + '"/>'
    note.content += '</en-note>'
    print note.content

    # Finally, send the new note to Evernote using the createNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    createdNote = noteStore.createNote(authToken, note)

    print "Successfully created a new note with GUID: ", createdNote.guid
