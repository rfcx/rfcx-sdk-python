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

    def authenticate(self,
                     persist=True,
                     persisted_credentials_path='.rfcx_credentials'):
        """Authenticate an RFCx user to obtain a token

        If you want to persist/load the credentials to/from a custom path then set `persisted_credentials_path`
        Args:
            persist: (optional, default= True) Should save the user token to the filesystem.
            persisted_credentials_path: (optional, default= '.rfcx_credentials') File path for saving user token.

        Returns:
            None.
        """
        auth = Authentication(persist, persisted_credentials_path)
        auth.authenticate()
        self.credentials = auth.credentials

    def download_segment(self,
                            stream,
                            dest_path,
                            start_time,
                            file_ext):
        """ Download single audio file (stream segment).
        Args:
            stream: (required) Identifier for stream/site
            dest_path: (required) Directory/folder path to save the file
            start_time: (required) Exact start timestamp (string or datetime) of the segment
            file_ext: (optional, default='wav') Audio file extension. Default to `wav`
        Returns:
            None.

        Raises:
            TypeError: if missing required arguments.
        """
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        return audio.download_segment(self.credentials.token, dest_path,
                                         stream, start_time, file_ext)

    def download_segments(self,
                             stream,
                             dest_path='./audios',
                             min_date=None,
                             max_date=None,
                             file_ext='wav',
                             parallel=True):
        """Download multiple audio in giving time range.

        Args:
            stream: (required) Identifies a stream/site
            dest_path: (optional, default= './audios') Directory/folder path to save the files
            min_date: (optional, default=None) Minimum timestamp to get the audio. If None then defaults to 30 days ago.
            max_date: (optional, default=None) Maximum timestamp to get the audio. If None then defaults to now.
            file_ext: (optional, default='wav') Audio file extension. Default to `wav`
            parallel: (optional, default=True) Parallel download audio. Defaults to True.

        Returns:
            None.
        """
        if self.credentials is None:
            print('Not authenticated')
            return

        if stream is None:
            print("stream cannot be None")
            return

        if min_date is None:
            min_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)

        if max_date is None:
            max_date = datetime.datetime.utcnow()

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        return audio.download_segments(self.credentials.token, dest_path,
                                          stream, min_date, max_date, file_ext, parallel)

    def projects(self,
                 keyword=None,
                 created_by=None,
                 only_public=None,
                 only_deleted=None,
                 fields=None,
                 limit=1000,
                 offset=0):
        """Retrieve a list of projects

        Args:
            keyword: (optional, default= None) Match project name with keyword
            created_by: (optional, default= None) The project owner. Have 3 options: None, me, or collaborator id
            only_public: (optional, default= None) Return only public projects
            only_deleted: (optional, default= None) Return only deleted projects
            fields: (optional, default=None) project information custom retrive fields.
            limit: (optional, default= 1000) Maximum number of  results to return
            offset: (optional, default= 0) Number of results to skip

        Returns:
            List of projects contains id, name, is_public, and external_id as default.
        """
        return api_rfcx.projects(self.credentials.token, keyword, created_by,
                                 only_public, only_deleted, fields, limit, offset)

    def stream(self, stream_id=None, fields=None):
        """ Retrieve a stream information

        Args:
            stream_id: (required) Identifies a stream/site.
            fields: (optional, default=None) stream information custom retrive fields.

        Returns:
            Stream contains id, name, description, start, end, project_id, project
            is_public, latitude, longitude, altitude, timezone, max_sample_rate, external_id,
            created_by_id, created_at, updated_at, and created_by fields as default.
        """
        if self.credentials is None:
            print('Not authenticated')
            return

        if stream_id is None:
            print('Require stream id')
            return

        return api_rfcx.stream(self.credentials, stream_id, fields)

    def streams(self,
                organizations=None,
                projects=None,
                created_by=None,
                name=None,
                keyword=None,
                include_public=False,
                include_deleted=False,
                fields=None,
                limit=1000,
                offset=0):
        """Retrieve a list of streams

        Args:
            organizations: (optional, default= None) List of organization ids
            projects: (optional, default= None) List of project ids
            created_by: (optional, default= None) The stream owner. Have 3 options: None, me, or collaborators
            name: (optional, default= None) Match exact streams with name (support *)
            keyword: (optional, default= None) Match stream name with keyword
            include_public: (optional, default=None) Include streams from public projects (that you aren't a member of)
            include_deleted: (optional, default=None) Include deleted streams
            fields: (optional, default=None) Specify fields to return (None will choose API default fields)
            limit: (optional, default= 1000) Maximum number of  results to return
            offset: (optional, default= 0) Number of results to skip

        Returns:
            List of streams contains id, name, description, start, end, project_id, project
            is_public, latitude, longitude, altitude, timezone, max_sample_rate, external_id,
            created_by_id, created_at, updated_at, created_by, and country_name as default.
        """

        if created_by is not None and created_by not in [
                "me", "collaborators"
        ]:
            print("created_by can be only None, me, or collaborators")
            return

        return api_rfcx.streams(self.credentials.token, organizations,
                                projects, created_by, name, keyword,
                                include_public, include_deleted, fields, limit, offset)

    def stream_segments(self,
                        stream,
                        start=None,
                        end=None,
                        limit=50,
                        offset=0):
        """Retrieve audio information about a specific stream

        Args:
            stream: (required) Identifies a stream/site.
            start: (optional, default= None) Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            end: (optional, default= None) Maximum timestamp of the audio. If None then defaults to now.
            limit: (optional, default= 50) Maximum results to return. Defaults to 50.
            offset: (optional, default= 0) Offset of the audio group.

        Returns:
            List of audio files contains id, start, end, and file extensions (meta data showing audio id and recorded timestamp).
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

        return api_rfcx.stream_segments(self.credentials.token, stream, start,
                                        end, limit, offset)

    def ingest_file(self, stream, filepath, timestamp):
        """ Ingest an audio to RFCx
        Args:
            stream: (required) Identifies a stream/site.
            filepath: (required) Local file path to be ingest.
            timestamp: (required) Audio timestamp in datetime type.

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
            start: (optional, default= None) Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            end: (optional, default= None) Maximum timestamp of the audio. If None then defaults to now.
            classifications: (optional, default=None) List of classification names e.g. orca, chainsaw.
            stream: (optional, default=None) Limit results to a given stream id.
            limit: (optional, default=50) Maximum number of results to be return.
            offset: (optional, default=0) Number of results to skip.

        Returns:
            List of annotations contains id, stream_id, start, end, frequency_min, and frequency_max.
        """

        if limit > 1000:
            raise Exception("Please give the value <= 1000")

        if start is None:
            start = util.date_before()
        if end is None:
            end = util.date_now()

        return api_rfcx.annotations(self.credentials.token, start, end,
                                    classifications, stream, limit, offset)

    def detections(self,
                   min_date=None,
                   max_date=None,
                   classifications=None,
                   classifiers=None,
                   streams=None,
                   min_confidence=None,
                   limit=50,
                   offset=0):
        """Retrieve a list of detections

        Args:
            min_date: (optional, default= None) Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            max_date: (optional, default= None) Maximum timestamp of the audio. If None then defaults to now.
            classifications: (optional, default=None) List of classification names e.g. orca, chainsaw.
            classifiers: (optional, default=None) List of classifier ids (integer) e.g. 93, 94.
            streams: (optional, default=None) List of stream ids.
            min_confidence (optional, default=None): Return the detection which equal or greater than given value. If None, it will use default in event strategy.
            limit: (optional, default=50) Maximum number of results to be return. The maximum value is 1000.
            offset: (optional, default=0) Number of results to skip.

        Returns:
            List of detections contains stream_id, start, end, confidence, and classification.
        """

        if limit > 1000:
            raise Exception("Please give the value <= 1000")

        if min_date is None:
            min_date = util.date_before()
        if max_date is None:
            max_date = util.date_now()

        return api_rfcx.detections(self.credentials.token, min_date, max_date,
                                   classifications, classifiers, streams,
                                   min_confidence, limit, offset)
