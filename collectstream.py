import sys
import spotipy
import spotipy.util as util
import time
import csv
import copy

OUTPUT_FILE = "played.csv"

class Song():

    def __init__(self, playback):
        self.timestamp =  playback['timestamp']
        self.name = playback['item']['name']
        self.album  = playback['item']['album']['name']
        self.artists = tuple([a['name'] for a in playback['item']['artists']])
        self.progress_ms = playback['progress_ms']
        self.duration = playback['item']['duration_ms']
        self.shuffle = playback['shuffle_state']
        self.repeat = playback['repeat_state']
        self.context = playback['context']['type']
        self.uri = playback['context']['uri']
    
    def get_tuple(self):
        return (self.timestamp, self.name, self.album, self.artists, self.progress_ms,
                self.duration, self.shuffle, self.repeat, self.context, self.uri)

def write_tuple(to_write):
    with open(OUTPUT_FILE, 'a') as f:
        w = csv.writer(f)
        w.writerow(to_write)

def main():
    scope = 'user-read-playback-state'

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    token = util.prompt_for_user_token(username, scope)

    sp = spotipy.Spotify(auth=token)
    last_request_time = time.time()
    playing = sp.current_playback
    print(playing)
    if playing is None:
        song = None
    else:
        song = Song(playing)
    print("STARTED")

    while True:
        if time.time() - last_request_time < 0.1:
            try:
                time.sleep(0.1 - (time.time() - last_request_time))
            except:
                pass
        
        try:
            playing = sp.current_playback()
            if playing is None:  # if nothing is playing
                if song is not None:
                    write_tuple(song.get_tuple())
                    song = None
                time.sleep(60)
                continue
            else:
                new_song = Song(playing)
                last_request_time = time.time()
        except Exception as e:
            print(e)
            time.sleep(1)
            continue

        if song is None:
            song = new_song
        elif song.name == new_song.name and song.artists == new_song.artists and song.album == new_song.album:
            song = new_song
        else:
            write_tuple(song.get_tuple())
            print("NEW SONG", new_song.name, "by", new_song.artists, "from", new_song.album)
            song = new_song

if __name__ == '__main__':
    main()