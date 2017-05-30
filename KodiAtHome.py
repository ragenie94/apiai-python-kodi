#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from flask import Flask
from flask import request
from flask import make_response

import os
import sys
import json
import apiai
from kodipydent import Kodi

# Flask app should start in global layout
app = Flask(__name__)

HOST = '192.168.2.118'
PORT = '8080'
USERNAME = 'kodi'
PASSWORD = 'password'
SORT = {"order": "ascending", "method": "title"}

CLIENT_ACCESS_TOKEN = 'b587fe1645ab47a98e58de785ca0bb5f'

def video(genre, details, firstName, lastName, mediaType):
    genreFilter = {}
    nameFilter = {}
    inprogressFilter = {}

    if genre != '' : 
        genreFilter['operator'] = 'is'
        genreFilter['field'] = 'genre'
        genreFilter['value'] = genre

    for detail in details:
        if (detail == 'actor' | detail == 'director'):
            nameFilter['operator'] = 'contains'
            nameFilter['field'] = detail

            if(firstName == '') : nameFilter['value'] = lastName
            elif(lastName == '') : nameFilter['value'] = firstName
            else : nameFilter['value'] = firstName + ' '+ lastName

        elif (detail == 'in progress') : 
            inprogressFilter['operator'] = 'true'
            inprogressFilter['field'] = 'inprogress'
            inprogressFilter['value'] = 'true'

    filterList = []

    if(len(nameFilter.items()) == 3) : filterList.append(nameFilter)
    if(len(genreFilter.items()) == 3) : filterList.append(genreFilter)
    if(len(inprogressFilter.items()) == 3) : filterList.append(inprogressFilter)

    finalFilter = {"and": filterList}
    if(mediaType == 'movie') : list = my_kodi.VideoLibrary.GetMovies(filter = finalFilter)
    elif(mediaType == 'tv') : list = my_kodi.VideoLibrary.GetTVShows(filter = finalFilter)

    genreFilter = None
    inprogressFilter = None
    nameFilter = None

    return list

def music(genre, details, artistName):
    genreFilter = {}
    nameFilter = {}

    if genre != '' : 
        genreFilter['operator'] = 'is'
        genreFilter['field'] = 'genre'
        genreFilter['value'] = genre

    if artistName != '':
        nameFilter['operator'] = 'is'
        nameFilter['field'] = 'artist'
        nameFilter['value'] = artistName

    filterList = []

    if(len(nameFilter.items()) == 3) : filterList.append(nameFilter)
    if(len(genreFilter.items()) == 3) : filterList.append(genreFilter)

    finalFilter = {"and": filterList}
    songs = my_kodi.AudioLibrary.GetSongs(filter = finalFilter)
    pass

@app.route('/webhook', methods=['POST'])
def main():
    my_kodi = Kodi(host = HOST, port = PORT, username = USERNAME, password = PASSWORD)
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    response = json.loads(request.getresponse().read())

    result = response['result']
    mediaType = result.get('media-types')

    if mediaType == 'music':
        music(artistName = result.get('music-artist'), genre = result.get('music-genre'), details = result.get('media-details'))
    elif mediaType == 'movie':
        video(genre = result.get('movie-genre'), details = result.get('media-details'), firstName = result.get('given-name'), lastName = result.get('last-name'), mediaType = mediaType)


    requestedMediaDetails = result.get('media-details')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')