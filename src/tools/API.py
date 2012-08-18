# -*- coding: utf-8 -*-


from filesystem.File import FileName
from getpass import getpass
from tools.Config import Config
import gdata.media
import gdata.photos
import gdata.photos.service
import time


class Text(unicode):

    def __new__(cls, sth):
        text = sth.text or ''
        return super(Text, cls).__new__(Text, text.strip(), 'utf8')


class API(object):
    """Picasa Web Albums API wrapper."""

    def __init__(self):
        self.__client = None

    @property
    def _client(self):
        if not self.__client:
            client = gdata.photos.service.PhotosService()
            client.email = Config().get('settings', 'email')
            client.password = self._prompt_password()
            client.source = 'Javorek-Elk-' + Config().get('application', 'version'),
            client.ProgrammaticLogin()
            self.__client = client
        return self.__client

    def _prompt_password(self):
        return getpass()

    def _get_albums(self):
        albums = self._client.GetUserFeed()
        for album in albums.entry:
            # https://gdata-python-client.googlecode.com/hg/pydocs/gdata.photos.html#AlbumData
            yield album

    def get_album(self, title):
        found = filter(lambda a: Text(a.title) == title, self._get_albums())
        if found:
            return found[0]

    def get_photo(self, album, filename):
        for photo in self.get_photos(album):
            if FileName(Text(photo.title)) == filename:
                return photo

    def set_info(self, album, title=None, timestamp=None, location=None, summary=None, access=None):
        if title:
            album.title.text = title
        if timestamp:
            # https://gdata-python-client.googlecode.com/hg/pydocs/gdata.photos.html#Timestamp
            # http://stackoverflow.com/questions/4559030/not-able-to-change-a-date-of-my-picasa-web-albums-album-via-python-api
            album.timestamp = gdata.photos.Timestamp(text='%d000' % time.mktime(timestamp))
        if location:
            album.location.text = location
        if summary:
            album.summary.text = summary
        if access:
            album.access.text = access

        return self._client.Put(album, album.GetEditLink().href, converter=gdata.photos.AlbumEntryFromString)

    def get_photos(self, album):
        photos = self._client.GetFeed('/data/feed/api/user/default/albumid/%s?kind=photo' % album.gphoto_id.text)
        for photo in photos.entry:
            yield photo

    def set_caption(self, photo, caption):
        if not photo.media:
            photo.media = gdata.media.Group()
        if not photo.media.description:
            photo.media.description = gdata.media.Description()

        photo.media.description.text = caption
        photo.summary.text = caption

        return self._client.UpdatePhotoMetadata(photo)

    def create_album(self, title, summary='', location=None):
        return self._client.InsertAlbum(title, summary, location, access='private')

    def upload_file(self, album, file, filename, summary='', content_type='image/jpeg'):
        try:
            return self._client.InsertPhotoSimple(album, filename, summary, file, content_type=content_type)
        except gdata.photos.service.GooglePhotosException:
            self._client.Delete(self.get_photo(album, filename))
            raise



