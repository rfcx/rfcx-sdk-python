"""RFCx client"""
import datetime
import os
import rfcx._audio as audio
import rfcx._ingest as ingest
import rfcx._util as util
import rfcx._api_rfcx as api_rfcx
from rfcx._authentication import Authentication


class Client(object):
    """Authenticate and perform requests against the RFCx platform"""
    def __init__(self):
        self.credentials = None
        self.default_site = None
        self.accessible_sites = None

    def authentication(self,
                       persist=True,
                       persisted_credentials_path='.rfcx_credentials'):
        """Authenticate an RFCx user to obtain a token

        If you want to persist/load the credentials to/from a custom path then set `persisted_credentials_path`
        Args:
            persist: Should save the user token to the filesystem (in file specified by
            persisted_credentials_path, defaults to .rfcx_credentials in the current directory).

        Returns:
            Success if an access_token was obtained
        """
        auth = Authentication(persist, persisted_credentials_path)
        auth.authentication()
        self.credentials = auth.credentials
        self.default_site = auth.default_site
        self.accessible_sites = auth.accessible_sites

    def download_file(self,
                      dest_path,
                      stream,
                      start_time,
                      end_time,
                      gain=1,
                      file_ext='wav'):
        """ Save audio to local path
        Args:
            dest_path: Audio save path.
            stream: Identifies a stream/site.
            start_time: Minimum timestamp to get the audio.
            end_time: Maximum timestamp to get the audio. (Should not more than 15 min range)
            gain: (optional, default = 1) Input channel tone loudness
            file_ext: (optional, default = 'wav') Extension for saving audio files.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.

        """
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        if not isinstance(start_time, datetime.datetime):
            print("start_time is not type datetime")
            return

        if not isinstance(end_time, datetime.datetime):
            print("end_time is not type datetime")
            return

        return audio.download_file(self.credentials.token, dest_path,
                                   stream, start_time, end_time, gain,
                                   file_ext)

    def stream_segments(self, stream, start, end, limit=50, offset=0):
        """Retrieve audio information about a specific stream

        Args:
            stream: (Required) Identifies a stream/site.
            start: Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the audio. If None then defaults to now.
            limit: Maximum results to return. Defaults to 50.
            offset: Offset of the audio group.

        Returns:
            List of audio files (meta data showing audio id and recorded timestamp)
        """
        if self.credentials is None:
            print('Not authenticated')
            return

        if stream is None:
            print('Require stream id')
            return

        if start is None:
            start = util.date_before()
        if end is None:
            end = util.date_now()

        return api_rfcx.stream_segments(self.credentials.token, stream,
                                        start, end, limit, offset)

    def download_file_segments(self,
                               dest_path=None,
                               stream=None,
                               min_date=None,
                               max_date=None,
                               gain=1,
                               file_ext='wav',
                               parallel=True):
        """Download audio using audio information from `stream_segments`

        Args:
            dest_path: (Required) Path to save audio.
            stream: (Required) Identifies a stream/site
            min_date: Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            max_date: Maximum timestamp of the audio. If None then defaults to now.
            gain: (optional, default= 1) Input channel tone loudness
            file_ext: (optional, default= 'wav') Audio file extension. Default to `wav`
            parallel: (optional, default= True) Parallel download audio. Defaults to True.

        Returns:
            None.
        """
        if self.credentials is None:
            print('Not authenticated')
            return

        if stream is None:
            print("Please specific the stream id.")
            return

        if min_date is None:
            min_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)

        if not isinstance(min_date, datetime.datetime):
            print("min_date is not type datetime")
            return

        if max_date is None:
            max_date = datetime.datetime.utcnow()

        if not isinstance(max_date, datetime.datetime):
            print("max_date is not type datetime")
            return

        if dest_path is None:
            if not os.path.exists('./audios'):
                os.makedirs('./audios')
            else:
                print(
                    '`audios` directory is already exits. Please specific the directory to save audio path or remove `audios` directoy'
                )
                return
        return audio.download_file_segments(self.credentials.token,
                                            dest_path, stream, min_date,
                                            max_date, gain, file_ext, parallel)

    def streams(self,
                organizations=None,
                projects=None,
                created_by=None,
                keyword=None,
                is_public=True,
                is_deleted=False,
                limit=1000,
                offset=0):
        """Retrieve a list of streams

        Args:
            organizations: List of organization ids
            projects: List of project ids
            created_by: The stream owner. Have 3 options: None, me, or collaborators
            keyword: Match streams name with keyword
            is_public: (optional, default=True) Match public or private streams
            is_deleted: (optional, default=False) Match deleted streams
            limit: (optional, default=1000) Maximum number of  results to return
            offset: (optional, default=0) Number of results to skip

        Returns:
            List of streams"""

        if created_by is not None and created_by not in [
                "me", "collaborators"
        ]:
            print("created_by can be only None, me, or collaborators")
            return

        return api_rfcx.streams(self.credentials.token, organizations,
                                projects, created_by, keyword, is_public,
                                is_deleted, limit, offset)

    def ingest_file(self, stream, filepath, timestamp):
        """ Ingest an audio to RFCx
        Args:
            stream: Identifies a stream/site
            filepath: Local file path to be ingest
            timestamp: Audio timestamp in datetime type

        Returns:
            None.
        """

        if not isinstance(timestamp, datetime.datetime):
            print("timestamp is not type datetime")
            return

        iso_timestamp = timestamp.replace(microsecond=0).isoformat() + 'Z'

        return ingest.ingest_file(self.credentials.token, stream, filepath,
                                  iso_timestamp)

    def annotations(self,
                    start=None,
                    end=None,
                    classifications=None,
                    stream=None,
                    limit=50,
                    offset=0):
        """Retrieve a list of annotations

        Args:
            start: Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the audio. If None then defaults to now.
            classifications: (optional, default=None) List of classification names e.g. orca, chainsaw.
            stream: (optional, default=None) Limit results to a given stream id.
            limit: (optional, default=50) Maximum number of results to be return.
            offset: (optional, default=0) Number of results to skip.

        Returns:
            List of annotations"""

        if limit > 1000:
            raise Exception("Please give the value <= 1000")

        if start == None:
            start = util.date_before()
        if end == None:
            end = util.date_now()

        return api_rfcx.annotations(self.credentials.token, start, end,
                                    classifications, stream, limit, offset)

    def detections(self,
                   start=None,
                   end=None,
                   classifications=None,
                   classifiers=None,
                   streams=None,
                   min_confidence=None,
                   limit=50,
                   offset=0):
        """Retrieve a list of detections

        Args:
            start: Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the audio. If None then defaults to now.
            classifications: (optional, default=None) List of classification names e.g. orca, chainsaw.
            classifiers: (optional, default=None) List of classifier ids (integer) e.g. 93, 94.
            streams: (optional, default=None) List of stream ids.
            min_confidence (optional, default=None): Return the detection which equal or greater than given value. If None, it will use default in event strategy.
            limit: (optional, default=50) Maximum number of results to be return. The maximum value is 1000.
            offset: (optional, default=0) Number of results to skip.

        Returns:
            List of detections"""

        if limit > 1000:
            raise Exception("Please give the value <= 1000")

        if start is None:
            start = util.date_before()
        if end is None:
            end = util.date_now()

        return api_rfcx.detections(self.credentials.token, start, end,
                                   classifications, classifiers, streams,
                                   min_confidence, limit, offset)
