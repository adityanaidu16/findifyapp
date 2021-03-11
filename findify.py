from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from spotipy.oauth2 import SpotifyClientCredentials
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import apology
import spotipy
import sys
import os
import time
from datetime import datetime

# Configure application
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if __name__ == "__main__":
    app.run(host= '0.0.0.0')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# set environmental variables with client id and secret key
os.environ['SPOTIPY_CLIENT_ID'] = '88eeb02578864648919647b7ccef1e08'
os.environ['SPOTIPY_CLIENT_SECRET'] = '89f3218d8dc143dd998aba6b2269037a'

@app.route("/")
def index():
    return render_template("index.html")

class MultiDict:
    def __init__(self):
        self.dict = {}

    def __setitem__(self, key, value):
        try:
            self.dict[key].append(value)
        except KeyError:
            self.dict[key] = [value]

    def __getitem__(self, key):
        return self.dict[key]


def artistloop(recommended_artists, relatedartists, sp, url, songname, performers):
    # iterate over every related artist
    for artist in relatedartists['artists']:
        # search for artist
        result = sp.search(q='artist:' + artist["name"], type='artist')

        # find number of followers for artist
        try:
            recommended_artists[artist["id"]] = "".join([(f"{result['artists']['items'][0]['followers']['total']:,d}"), " Followers"])
        except:
            recommended_artists[artist["id"]] = ""
        #print(recommended_artists[artist["id"]][0]) #replacing followers dict

        # find genres for artist
        try:
            recommended_artists[artist["id"]] = "".join([result['artists']['items'][0]['genres'][0], ", ", result['artists']['items'][0]['genres'][1]])
        except:
            recommended_artists[artist["id"]] = ""
        #print(recommended_artists[artist["id"]][1]) # replacing genres dict

        # find artist's top tracks
        trax = sp.artist_top_tracks(artist["uri"])

        # iterate over every track in artist's top tracks list
        for track in trax['tracks']:
            # collect data
            try:
                artist["name"] = artist["name"].replace('"', "™").replace("'", "®")
                url[artist["name"]] = track['preview_url']
                songname[artist["uri"]] = track['name'].replace("'", "®").replace('"', "™")
                meta = sp.track(track["id"])
                performers[artist["uri"]] = [artist['name'] for artist in meta['artists']]
                performers[artist["uri"]] = ( ", ".join( str(e) for e in performers[artist["uri"]] ) )
                performers[artist["uri"]] = performers[artist["uri"]].replace("'", "®").replace('"', "™")
                if not track['preview_url']:
                    raise Exception('Preview not found')
                recommended_artists[artist["id"]] = "column"
                break
            except:
                continue
        # if none of user's top 10 tracks are available for preview:
        else:
            songname[artist["uri"]] = trax['tracks'][0]['name'].replace("'", "®").replace('"', "™")
            meta = sp.track(trax["tracks"][0]["id"])
            performers[artist["uri"]] = [artist['name'] for artist in meta['artists']]
            performers[artist["uri"]] = ( ", ".join( str(e) for e in performers[artist["uri"]] ) ).replace("'", "®").replace('"', "™")
            recommended_artists[artist["id"]] = "column2"
            url[artist["name"]] = 'None'


@app.route("/getartists", methods=["GET", "POST"])
def getartists():
    """Similar Artists"""

    # User reach route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # start timer
        total_start_time = time.time()

        # request user input from HTML form
        artist_name = request.form.get("artist_name")

        # check if user input is empty
        if artist_name == "":
            return apology("enter an artist", 403)

        # client credentials setup
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # search for artist using user input
        result = sp.search(q='artist:' + artist_name, type='artist')
        try:
            # assign artist name and uri to variables
            name = result['artists']['items'][0]['name']
            uri = result['artists']['items'][0]['uri']

            # search for related artists
            relatedartists = sp.artist_related_artists(uri)

            # Flash alert
            flash("Recommended artists based on " + name)

            # setup dictionaries and lists
            recommended_artists = MultiDict()
            url, songname, performers = {}, {}, {}

            artistloop(recommended_artists, relatedartists, sp, url, songname, performers)

        # error in getting information about user inputted artist
        except BaseException:
            return apology("artist not found", 403)

        # find total duration of function and write it in runtimes.txt
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        timefile = open("static/runtimes.txt", "a")
        timefile.write(str(total_time) + '\n')
        timefile.close()

        # display recommended artists to user
        return render_template("displayartists.html", relatedartists=relatedartists, recommended_artists=recommended_artists, url=url, songname=songname, performers=performers)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("getartists.html")



def trackloop(recommended_tracks, recommendations, sp):
    for track in recommendations["tracks"]:
        try:
            # find cover art for track
            albumResults = sp.album(track['album']['id'])
            recommended_tracks[track["id"]] = albumResults['images'][0]['url']
            #print(recommended_tracks[track["id"]][0])

            try:
                # get release date
                date = datetime.strptime(albumResults['release_date'], "%Y-%m-%d")
                year = date.year
                recommended_tracks[track["id"]] = "".join ([date.strftime("%b"), " ", str(year)])
                #print(recommended_tracks[track["id"]][1])
            except:
                recommended_tracks[track["id"]] = albumResults['release_date']

            # get track's artists
            meta = sp.track(track["id"])
            recommended_tracks[track["id"]] = ( ", ".join( str(e) for e in ([artist['name'] for artist in meta['artists']]) ) ).replace("'", "®").replace('"', "™")
            #print(recommended_tracks[track["id"]][2])

            # get track name and replace apostrophes and quotations
            recommended_tracks[track["id"]] = track['name'].replace("'", "®").replace('"', "™")
            #print(recommended_tracks[track["id"]][3])

            # check if track has available audio preview
            if not track['preview_url']:
                    raise Exception('Preview not found')

            # set opacity to column (making it clear)
            recommended_tracks[track["id"]] = "column"
            #print(recommended_tracks[track["id"]][4])

        # track is unavailable for preview
        except:
            # set opacity to column2 (making it opaque/faded)
            recommended_tracks[track["id"]] = "column2"



@app.route("/gettracks", methods=["GET", "POST"])
def gettracks():
    """Similar Tracks"""

    # User reach route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # start timer
        total_start_time = time.time()

        # client credentials setup
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        try:
            # initialize list for all user's inputted tracks (up to 5) || initialize list for displaying user's inputted tracks as alert
            tracks, names = [], []

            # request user input from HTML form
            uinput  = request.form.get("input1")

            # check if user input is empty
            if uinput == "":
                    return apology("enter a track", 403)

            # find track names and artist names, and append to tracks[] and names[]
            track = sp.search(q='track:' + uinput, type='track')
            uri = track['tracks']['items'][0]['uri']
            name = track['tracks']['items'][0]['name']
            a1 = track['tracks']['items'][0]['artists'][0]['name']
            name = " ".join ([name, "by", a1])
            names.append(name)
            tracks.append(uri)

            # repeat above for user input 2-5
            x=2
            while x<6:
                uinput  = request.form.get("input" + str(x))
                x+=1
                if uinput!="Track Name":
                    if uinput == "":
                        return apology("Do not leave fields empty", 403)
                    else:
                        try:
                            track = sp.search(q='track:' + uinput, type='track')
                            uri = track['tracks']['items'][0]['uri']
                            name = track['tracks']['items'][0]['name']
                            a1 = track['tracks']['items'][0]['artists'][0]['name']
                            name = " ".join ([name, "by", a1])
                            names.append(name)
                            tracks.append(uri)
                        except:
                            pass

            # set and alert names[]
            names = ( ",  ".join( str(e) for e in names ) )
            flash(" ".join (["Recommended songs based on ", names]))

            # initialize dictionaries
            recommended_tracks = MultiDict()

            # find recommended songs based on user-inputted track(s)
            recommendations = sp.recommendations(seed_tracks=tracks)

            trackloop(recommended_tracks, recommendations, sp)
            # iterate over every recommended track


        # error in getting user-inputted track(s)
        except BaseException:
            return apology("track not found", 403)

        # find total duration of function and write it in runtimes.txt
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        timefile = open("static/runtimes.txt", "a")
        timefile.write(str(total_time) + '\n')
        timefile.close()

        # display recommended songs to user
        return render_template("displaytracks.html", recommended_tracks=recommended_tracks, recommendations=recommendations)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("gettracks.html")

