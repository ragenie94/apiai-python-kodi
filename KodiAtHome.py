#!/usr/bin/env python

from __future__ import print_function
#from urllib.parse import urlparse, urlencode
#from urllib.request import urlopen, Request
#from urllib.error import HTTPError
from flask import Flask
from flask import request
from flask import make_response

import string
import os
import sys
import json
import apiai
from kodipydent import Kodi

# Flask app should start in global layout
app = Flask(__name__)

HOST = '192.228.162.157'
PORT = '8080'
USERNAME = 'kodi'
PASSWORD = 'rajinimohan'
my_kodi = Kodi(HOST, port = PORT, username = USERNAME, password = PASSWORD)
#SORT = {"order": "ascending", "method": "title"}

CLIENT_ACCESS_TOKEN = 'b587fe1645ab47a98e58de785ca0bb5f'

@app.route('/webhook', methods=['POST'])
def main():
    req = request.get_json(silent=True, force=True) #get POST from API.ai
    print(json.dumps(req, indent=4))

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN) #allow sending responses back

    result = req['result']
    action = result.get('action')
    details = result.get('parameters').get('media-details')
    firstName = result.get('parameters').get('given-name')
    lastName = result.get('parameters').get('last-name')

    print(details)
    print(firstName)
    print(lastName)

    searchResult = {}
    if action == 'search.music':
        artistName = result.get('parameters').get('music-artist')
        musicGenre = result.get('parameters').get('music-genre')
        print(artistName)
        print(musicGenre)
        searchResult = musicSearch(artistName = artistName, genre = musicGenre, details = details)
    elif action == 'search.video':
        mediaType = result.get('parameters').get('media-types')
        movieGenre = result.get('parameters').get('movie-genre')
        print(mediaType)
        print(movieGenre)
        searchResult = videoSearch(genre = movieGenre, details = details, firstName = firstName, lastName = lastName, mediaType = mediaType)

    result = searchResult['result']
    limits = result['limits']
    totalResults = limits['total']
    if(totalResults != None) :
        speech = "Found %d matches" %(totalResults)
    elif totalResults == '0':
        speech = "There isn't anything that matches your criteria"
    else : speech = "There has been an error"

    response = {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "raj-apiai-python-kodi"
    }

    res = json.dumps(response, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def videoSearch(genre, details, firstName, lastName, mediaType):
    genreFilter = {}
    nameFilter = {}
    inprogressFilter = {}

    if genre != '' : 
        genreFilter['operator'] = 'is'
        genreFilter['field'] = 'genre'
        genreFilter['value'] = genre

    for detail in details:
        print(detail)
        if (detail == 'actor') or (detail == 'director'):
            nameFilter['operator'] = 'contains'
            nameFilter['field'] = detail

            #Kodi is space sensitive, so no space at the end
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
    if(mediaType == 'movie') : videoList = my_kodi.VideoLibrary.GetMovies(filter = finalFilter)
    elif(mediaType == 'tv') : videoList = my_kodi.VideoLibrary.GetTVShows(filter = finalFilter)

    #clear the dicts, ready to be reused
    genreFilter = None
    inprogressFilter = None
    nameFilter = None

    return videoList

def musicSearch(genre, details, artistName):
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

    #make sure the filters are created before compiling them
    #a correct filter would have 3 items in it
    if(len(nameFilter.items()) == 3) : filterList.append(nameFilter)
    if(len(genreFilter.items()) == 3) : filterList.append(genreFilter)

    finalFilter = {"and": filterList} #use 'and' operator to consider every filter
    songList = my_kodi.AudioLibrary.GetSongs(filter = finalFilter) #get search result from Kodi box

    #clear the dicts, ready to be reused
    genreFilter = None
    nameFilter = None

    return songList

#I have no idea what this is for
if __name__ == '__main__':
    #main()
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')