import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class SpotifyExtractor:
    def __init__(self):
        """Initialize Spotify client with OAuth"""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        
        # Required scopes for your data
        scope = "user-read-recently-played user-top-read user-library-read playlist-read-private"
        
        # Initialize Spotify client
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scope
        ))
        
        print("✅ Spotify client initialized successfully!")
    
    def get_recently_played(self, limit=50):
        """Get recently played tracks"""
        try:
            results = self.sp.current_user_recently_played(limit=limit)
            print(f"✅ Retrieved {len(results['items'])} recently played tracks")
            return results
        except Exception as e:
            print(f"❌ Error getting recently played: {e}")
            return None
    
    def get_top_tracks(self, time_range='medium_term', limit=50):
        """Get top tracks for a time period
        time_range options: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
        """
        try:
            results = self.sp.current_user_top_tracks(time_range=time_range, limit=limit)
            print(f"✅ Retrieved {len(results['items'])} top tracks ({time_range})")
            return results
        except Exception as e:
            print(f"❌ Error getting top tracks: {e}")
            return None
    
    def get_top_artists(self, time_range='medium_term', limit=50):
        """Get top artists for a time period"""
        try:
            results = self.sp.current_user_top_artists(time_range=time_range, limit=limit)
            print(f"✅ Retrieved {len(results['items'])} top artists ({time_range})")
            return results
        except Exception as e:
            print(f"❌ Error getting top artists: {e}")
            return None
    
    def get_audio_features(self, track_ids):
        """Get audio features for a list of track IDs"""
        try:
            # Spotify API limits to 100 tracks at a time
            features = []
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                batch_features = self.sp.audio_features(batch)
                features.extend([f for f in batch_features if f is not None])
            
            print(f"✅ Retrieved audio features for {len(features)} tracks")
            return features
        except Exception as e:
            print(f"❌ Error getting audio features: {e}")
            return []
    
    def get_saved_tracks(self, limit=50):
        """Get user's saved tracks (liked songs)"""
        try:
            results = self.sp.current_user_saved_tracks(limit=limit)
            print(f"✅ Retrieved {len(results['items'])} saved tracks")
            return results
        except Exception as e:
            print(f"❌ Error getting saved tracks: {e}")
            return None
    
    def extract_all_data(self):
        """Extract all data types and return as dictionary"""
        print("🎵 Starting Spotify data extraction...")
        
        data = {}
        
        # Get recently played
        data['recently_played'] = self.get_recently_played()
        
        # Get top items for different time ranges
        data['top_tracks_short'] = self.get_top_tracks('short_term')
        data['top_tracks_medium'] = self.get_top_tracks('medium_term') 
        data['top_tracks_long'] = self.get_top_tracks('long_term')
        
        data['top_artists_short'] = self.get_top_artists('short_term')
        data['top_artists_medium'] = self.get_top_artists('medium_term')
        data['top_artists_long'] = self.get_top_artists('long_term')
        
        # Get saved tracks
        data['saved_tracks'] = self.get_saved_tracks()
        
        # Collect all unique track IDs for audio features
        track_ids = set()
        
        # From recently played
        if data['recently_played']:
            for item in data['recently_played']['items']:
                track_ids.add(item['track']['id'])
        
        # From top tracks
        for key in ['top_tracks_short', 'top_tracks_medium', 'top_tracks_long']:
            if data[key]:
                for item in data[key]['items']:
                    track_ids.add(item['id'])
        
        # From saved tracks
        if data['saved_tracks']:
            for item in data['saved_tracks']['items']:
                track_ids.add(item['track']['id'])
        
        # Get audio features for all tracks
        data['audio_features'] = self.get_audio_features(list(track_ids))
        
        print(f"🎉 Data extraction complete! Found {len(track_ids)} unique tracks")
        return data
    
    def save_to_json(self, data, filename=None):
        """Save extracted data to JSON file for inspection"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spotify_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Data saved to {filename}")


# Test the extractor
if __name__ == "__main__":
    # Initialize extractor
    extractor = SpotifyExtractor()
    
    # Test with a small sample first
    print("\n🧪 Testing with recently played tracks...")
    recent = extractor.get_recently_played(limit=5)
    
    if recent:
        print(f"\nSample track: {recent['items'][0]['track']['name']} by {recent['items'][0]['track']['artists'][0]['name']}")
        print("✅ Spotify connection working!")
        
        # Uncomment below to run full extraction
        # print("\n🚀 Running full extraction...")
        # all_data = extractor.extract_all_data()
        # extractor.save_to_json(all_data)
    else:
        print("❌ Connection failed - check your credentials")