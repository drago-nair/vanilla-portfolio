#!/opt/hermes/.venv/bin/python
"""Get currently playing track from Spotify and output as JSON."""
import sys, json, time
sys.path.insert(0, '/opt/hermes')

from plugins.spotify.client import SpotifyClient, SpotifyAuthRequiredError

def main():
    try:
        client = SpotifyClient()
        result = client.get_currently_playing()
    except SpotifyAuthRequiredError as e:
        result = {'error': 'auth_required', 'message': str(e)}
    except Exception as e:
        result = {'error': type(e).__name__, 'message': str(e)}

    # If it's the "empty" response, nothing is playing
    if isinstance(result, dict) and result.get('empty'):
        output = {
            "name": "",
            "artist": "",
            "imageURL": "",
            "href": "",
            "isPlayingNow": False,
            "updatedAt": int(time.time())
        }
    elif isinstance(result, dict) and result.get('error'):
        # Auth or other error - write nothing-playing to be safe, preserve file
        print(json.dumps(result, indent=2), file=sys.stderr)
        output = None  # Don't overwrite
    else:
        # Extract fields
        item = result.get('item') or {}
        name = item.get('name', '')
        artists = item.get('artists', [])
        artist_str = ', '.join(a.get('name', '') for a in artists if a.get('name'))
        images = item.get('album', {}).get('images', [])
        image_url = images[0]['url'] if images else ''
        external_urls = item.get('external_urls', {})
        href = external_urls.get('spotify', '')
        is_playing = bool(result.get('is_playing', False))

        output = {
            "name": name,
            "artist": artist_str,
            "imageURL": image_url,
            "href": href,
            "isPlayingNow": is_playing,
            "updatedAt": int(time.time())
        }

    if output:
        print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
