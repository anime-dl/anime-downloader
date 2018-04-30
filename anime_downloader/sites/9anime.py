from .anime import BaseAnime, BaseEpisode

class NineAnime(BaseAnime):
    # episodes = soup.find_all('ul', ['episodes'])
    # if episodes == []:
    #     err = 'No episodes found in url "{}"'.format(self.url)
    #     if self._callback:
    #         self._callback(err)
    #     args = [self.url]
    #     raise NotFoundError(err, *args)
    # episodes = episodes[:int(len(episodes)/3)]
    #
    # for x in episodes:
    #     for a in x.find_all('a'):
    #         ep_id = a.get('data-id')
    #         self._episodeIds.append(ep_id)
