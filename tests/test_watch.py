from anime_downloader.watch import Watcher as Watcher_


class Watcher(Watcher_):
    _TEST_LIST = []

    def _append_to_watch_file(self, anime):
        self._TEST_LIST.append(anime)

    def _write_to_watch_file(self, animes):
        self._TEST_LIST = animes

    def _read_from_watch_file(self):
        return self._TEST_LIST


class TestWatcher:
    def setup(self):
        self.watch = Watcher()

    def test_new(self):
        self.watch.new('https://www5.9anime.is/watch/naruto.xx8z')
        self.watch.new('https://www5.9anime.is/watch/naruto-shippuden.qv3')

        assert len(self.watch._TEST_LIST) == 2

    def test_get(self):
        anime = self.watch.get('shippu')
        assert anime.title.lower() == 'naruto: shippuden'

    def test_update(self):
        anime = self.watch.get('shippu')
        anime.episodes_done += 1
        self.watch.update(anime)
        anime_update = self.watch.get('shippu')
        assert anime_update.episodes_done == 1

    def test_remove(self):
        anime = self.watch.get('shippu')
        self.watch.remove(anime.title)
        assert len(self.watch._TEST_LIST) == 1
