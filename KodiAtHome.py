#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import json
import apiai
import kodipydent

HOST = '192.168.2.118'
PORT = '8080'
USERNAME = 'kodi'
PASSWORD = 'password'
my_kodi = Kodi(host = HOST, port = PORT, username = USERNAME, password = PASSWORD)
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

def main():
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
    main()