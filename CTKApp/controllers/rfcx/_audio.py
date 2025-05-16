"""RFCx audio segment information and download"""
import datetime
import shutil
import os
import sys
sys.path.append(os.path.dirname(__file__))
import concurrent.futures
import requests
import _api_rfcx as api_rfcx
import threading
import tempfile
import json


def __save_file(url, local_path, token, stop_flag):
    """ Download the file from url and save it locally under local_path """
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        with requests.get(url, headers=headers, stream=True, timeout=10) as response:
            for chunk in response.iter_content(chunk_size=8192):
                if stop_flag.is_set():
                    print("Download cancelled")
                    break
                # Process chunk here
    except Exception as e:
        stop_flag.set()
        raise Exception(f"Network error when accessing {url}: {e}")

    if response.status_code == 200:
        with open(local_path, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
            print(f'Saved {local_path}')
    else:
        print('Cannot download', url)
        reason = response.json()
        print('Reason:', response.status_code, reason['message'])
        raise Exception(
            f"Failed to download from {url}. "
            f"Status code: {response.status_code}. Reason: {reason['message']}"
        )


def __local_audio_file_path(path, audio_name, audio_extension):
    """ Create string for the name and the path """
    return path + '/' + audio_name + '.' + audio_extension.lstrip('.')


def __generate_date_in_isoformat(date):
    """ Generate date in iso format ending with `Z` """
    return date.replace(microsecond=0).isoformat() + 'Z'


def __iso_to_rfcx_custom_format(time):
    """Convert RFCx iso format to RFCx custom format"""
    return time.replace('-', '').replace(':', '').replace('.', '')


def __get_all_segments(token, stream_id, start, end):
    """Get all audio segment in the `start` and `end` time range"""
    all_segments = []
    empty_segment = False
    offset = 0

    while not empty_segment:
        # No data will return empty array from server
        segments = api_rfcx.stream_segments(token,
                                   stream_id,
                                   start,
                                   end,
                                   limit=1000,
                                   offset=offset)
        if segments:
            all_segments.extend(segments)
            offset = offset + 1000
        else:
            empty_segment = True

    return all_segments


def __download_segment(token, save_path, stream_id, start_str, file_ext, stop_flag):
    audio_name = stream_id + '_' + start_str.replace('.000Z', '').replace('Z', '').replace(':', '-').replace('.', '-').replace('T', '_')
    url = f'{api_rfcx.base_url}/streams/{stream_id}/segments/{start_str}/file'
    local_path = __local_audio_file_path(save_path, audio_name, file_ext)
    try:
        __save_file(url, local_path, token, stop_flag)
    except Exception as e:
        raise Exception(f"Network error while downloading segment {start_str}: {e}") from e
    return local_path


def download_segment(token,
                        dest_path,
                        stream_id,
                        start,
                        file_ext,
                        stop_flag=None):
    """ Download a single audio file (segment)
        Args:
            dest_path: Audio save path.
            stream_id: Stream id to get the segment.
            start: Exact start timestamp (string or datetime).
            file_ext: Extension for saving audio files.

        Returns:
            Path to downloaded file.

        Raises:
            TypeError: if missing required arguments.
    """
    if stop_flag and stop_flag.is_set():
        return None
    if isinstance(start, datetime.datetime):
        start = __generate_date_in_isoformat(start)
    return __download_segment(token, dest_path, stream_id, start, file_ext)


def download_segments(token,
                     dest_path,
                     stream_id,
                     min_date,
                     max_date,
                     file_ext='wav',
                     parallel=True,
                     max_workers=100):
    """ Download a set of audio files (segments) falling within a date range
        Args:
            token: RFCx client token.
            dest_path: Audio save path.
            stream_id: Identifies a stream/site
            min_date: Minimum timestamp to get the audio.
            max_date: Maximum timestamp to get the audio.
            file_ext: (optional, default= 'wav') Extension for saving audio file.
            parallel: (optional, default= True) Enable to parallel download audio from RFCx.
            max_workers: (optional, default= 100) Maximum number of parallel downloads.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguments
            Exception: if downloads fail with first error in the list
    """
    stream_resp = api_rfcx.stream(token, stream_id)
    if stream_resp is None:
        return

    stream_name = stream_resp['name']
    if isinstance(min_date, datetime.datetime):
        min_date = __generate_date_in_isoformat(min_date)
    if isinstance(max_date, datetime.datetime):
        max_date = __generate_date_in_isoformat(max_date)

    segments = __get_all_segments(token, stream_id, min_date, max_date)
    
    if not segments:
        print(f'No data found on {min_date[:10]} - {max_date[:10]} at {stream_name}')
        return

    print(f'Found {len(segments)} audio segments from {stream_name}')
    
    # Normalize all paths to use forward slashes
    dest_path = os.path.normpath(dest_path)
    save_path = os.path.normpath(os.path.join(dest_path, stream_name))
    os.makedirs(save_path, exist_ok=True)
    
    # Setup tracking directory with safe path handling
    temp_dir = os.path.normpath(os.path.join(dest_path, '.temp_downloads'))
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create safe filenames for tracking files
    safe_stream_id = "".join(c for c in stream_id if c.isalnum() or c in ('-', '_'))
    tracking_filename = f'{safe_stream_id}_{min_date[:10]}_{max_date[:10]}.tracking'
    tracking_file = os.path.normpath(os.path.join(temp_dir, tracking_filename))
    
    # Load existing tracking data if exists
    completed_segments = set()
    if os.path.exists(tracking_file):
        try:
            with open(tracking_file, 'r') as f:
                tracking_data = json.load(f)
                completed_segments = set(tracking_data.get('completed', []))
        except Exception as e:
            print(f"Warning: Failed to load tracking file {tracking_file}: {e}")

    # Filter segments to only those not completed
    pending_segments = [s for s in segments if s['start'] not in completed_segments]
    
    if not pending_segments:
        print(f'All segments already downloaded for {stream_name}')
        # Clean up tracking file if all segments are downloaded
        if os.path.exists(tracking_file):
            try:
                os.remove(tracking_file)
            except Exception as e:
                print(f"Warning: Could not remove tracking file {tracking_file}: {e}")
        return
    
    print(f'Downloading {len(pending_segments)} remaining audio segments from {stream_name}')
    
    stop_flag = threading.Event()
    errors = []
    
    def update_tracking(segment_start, success):
        """Update tracking file with download status"""
        try:
            tracking_data = {'completed': list(completed_segments)}
            if success:
                tracking_data['completed'].append(segment_start)
            
            with open(tracking_file, 'w') as f:
                json.dump(tracking_data, f)
        except Exception as e:
            print(f"Warning: Failed to update tracking file {tracking_file}: {e}")

    def download_wrapper(segment):
        """Wrapper function to handle tracking and errors"""
        if stop_flag.is_set():
            return
        
        segment_start = segment['start']
        try:
            # Create temp file path
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Perform the actual download
                result = __download_segment(token, save_path, stream_id, segment_start, file_ext, stop_flag)
                
                # Mark as completed
                completed_segments.add(segment_start)
                update_tracking(segment_start, True)
                
                return result
            finally:
                # Clean up temp file if it exists
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(f"Warning: Could not remove temp file {temp_path}: {e}")
        except Exception as e:
            errors.append((segment_start, str(e)))
            stop_flag.set()
            return None

    try:
        if parallel:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(download_wrapper, segment): segment for segment in pending_segments}
                
                for future in concurrent.futures.as_completed(futures):
                    if stop_flag.is_set():
                        # Cancel remaining futures if error occurred
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        break
        
        else:
            for segment in pending_segments:
                if stop_flag.is_set():
                    break
                download_wrapper(segment)
        
        if errors:
            # Save failed downloads information with safe filename
            error_filename = f'{safe_stream_id}_{min_date[:10]}_{max_date[:10]}.errors'
            error_file = os.path.normpath(os.path.join(temp_dir, error_filename))
            try:
                with open(error_file, 'w') as f:
                    json.dump(errors, f)
            except Exception as e:
                print(f"Warning: Could not save error file {error_file}: {e}")
            
            # Raise exception with first error
            first_error = errors[0][1] if errors else "Unknown error"
            raise Exception(f"{len(errors)} segment(s) failed to download. First error: {first_error}")
        else:
            # Clean up tracking file if all successful
            if os.path.exists(tracking_file):
                try:
                    os.remove(tracking_file)
                except Exception as e:
                    print(f"Warning: Could not remove tracking file {tracking_file}: {e}")
            print(f'Successfully downloaded all segments from {stream_name}')
            
    except Exception as e:
        print(f"Download interrupted: {str(e)}")
        raise Exception(f"Download interrupted for site {stream_name} ({stream_id}): {str(e)}")
    finally:
        # Clean up any remaining temp files
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                if f.startswith('tmp'):
                    try:
                        os.remove(os.path.normpath(os.path.join(temp_dir, f)))
                    except Exception as e:
                        print(f"Warning: Could not remove temp file {f}: {e}")
