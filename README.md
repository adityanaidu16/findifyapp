# Findify

### DESCRIPTION
[Findify](https://findifyapp.herokuapp.com/) was my CS50 final project, and can recommend artists and songs based on users' input, while also allowing users to preview music. All of this is accomplished using Spotify's Web API.
The use of this web application is *recommended on a PC* rather than a mobile device due to it's use of hovering functions.


### FEATURES
In ***Artist Recommendations***, the user can input an artist's name, returning 20 similar artists' images. Hovering over an artist shows the artist's name, plays a preview of a top track by them, and displays the track's artists,
artist's number of followers on Spotify, and artist's top two genres. Noticeably, some artists' images are less opaque than others; this is because *these artists' audio previews are unavailable*, however
every other function, including the ability to click on an image and return other similar artists, is still available.

![Artist Recommendations Image](/static/artistrecommendations.gif)

In ***Song Recommendations***, the user can input up to 5 songs (by clicking the plus button to add more fields), returning 20 similar songs, shown by their cover art. Hovering over a song shows the song's name, displays the song's artist(s), and plays a preview of it.
Noticeably, some songs' images are less opaque than others; this is because *these artists' audio previews are unavailable*, however every other function, including the ability to click and return other similar tracks, is still available.
It is helpful and improves accuracy of the search to include the artist name or album name after the track name in your input, in order to differentiate from other simliarly-named songs.

![Song Recommendations Image](/static/songrecommendations.gif)

### AUTHENTICATION
Authentication is done though Spotipy with the [Client Credentials Flow](https://spotipy.readthedocs.io/en/2.16.0/#client-credentials-flow).

![Client Credentials Flow Chart](https://developer.spotify.com/assets/AuthG_ClientCredentials.png)

### DEVELOPER TOOLS
Available in /static/ is a text file containing a constantly-updating list of the runtimes of the query (from the time the user submits input to the time the user receives an output).

### TECHNOLOGIES & FRAMEWORKS
- Python (Flask)
- HTML, CSS (Bootstrap)
- Javascript
