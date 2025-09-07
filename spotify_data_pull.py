import os
import requests
import csv

def get_top_tracks_for_period(time_range, headers, max_tracks=200):
    all_tracks = []
    url = 'https://api.spotify.com/v1/me/top/tracks'
    offset = 0
    limit = 50
    
    while len(all_tracks) < max_tracks:
        params = {
            'limit': limit,
            'offset': offset,
            'time_range': time_range
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error for {time_range}: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        tracks = data.get('items', [])
        
        if not tracks:
            break
            
        # Add time_range and rank to each track
        for i, track in enumerate(tracks):
            track['time_range'] = time_range
            track['rank'] = offset + i + 1
            
        all_tracks.extend(tracks)
        offset += limit
        
        if len(tracks) < limit:
            break
    
    return all_tracks

def get_all_top_tracks():
    token = "ADD YOUR TOKEN"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    all_tracks = []
    time_ranges = ['short_term', 'medium_term', 'long_term']
    
    for time_range in time_ranges:
        print(f"Fetching top 100 tracks for {time_range}...")
        tracks = get_top_tracks_for_period(time_range, headers, 100)
        all_tracks.extend(tracks)
        print(f"Got {len(tracks)} tracks for {time_range}")
    
    return {'items': all_tracks}

def get_artist_details(artist_ids, headers):
    artist_details = {}
    
    # Process in batches of 50 (API limit)
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i+50]
        ids_str = ','.join(batch)
        
        url = 'https://api.spotify.com/v1/artists'
        params = {'ids': ids_str}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for artist in data['artists']:
                artist_details[artist['id']] = artist
        else:
            print(f"Error getting artist details: {response.status_code}")
    
    return artist_details

def write_to_csv(tracks_data, artist_details):
    num_tracks = len(tracks_data['items'])
    filename = f'top_{num_tracks}_songs_simple.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Rank', 'Time Range', 'Artist', 'Song Title', 'Album', 'Release Date', 'Duration (ms)', 
            'Popularity', 'Explicit', 'Track ID', 'Artist Genres', 'Artist Popularity'
        ])
        
        for track in tracks_data['items']:
            time_range = track.get('time_range', '')
            rank = track.get('rank', '')
            artist = track['artists'][0]['name']
            artist_id = track['artists'][0]['id']
            song_title = track['name']
            album = track['album']['name']
            release_date = track['album']['release_date']
            duration = track['duration_ms']
            popularity = track['popularity']
            explicit = track['explicit']
            track_id = track['id']
            
            # Get artist details
            artist_info = artist_details.get(artist_id, {})
            genres = ', '.join(artist_info.get('genres', []))
            artist_popularity = artist_info.get('popularity', '')
            
            writer.writerow([
                rank, time_range, artist, song_title, album, release_date, duration, popularity, 
                explicit, track_id, genres, artist_popularity
            ])
    
    print(f"Top {num_tracks} songs written to {filename}")

if __name__ == "__main__":
    tracks_data = get_all_top_tracks()
    if tracks_data:
        token = "ADD YOUR TOKEN"
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get artist IDs
        artist_ids = list(set([track['artists'][0]['id'] for track in tracks_data['items']]))
        
        print(f"Fetching artist details for {len(artist_ids)} artists...")
        artist_details = get_artist_details(artist_ids, headers)
        
        write_to_csv(tracks_data, artist_details)