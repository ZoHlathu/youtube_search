import requests
import urllib.parse
import json

class YoutubeSearch:
    def __init__(self, search_terms: str, max_results=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = self._search()

    def _search(self):
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        BASE_URL = "https://youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"
        response = requests.get(url).text
        while "ytInitialData" not in response:
            response = requests.get(url).text
        try:
            results = self._parse_html(response)
        except IndexError:
            results = []
        if self.max_results is not None and len(results) > self.max_results:
            return results[:self.max_results]
        return results

    def _parse_html(self, response):
        results = []
        start = response.find("ytInitialData")
        if start != -1:
            start += len("ytInitialData")
            end = response.find("};", start) + 1
            if end != -1:
                json_str = response[start:end]
                data = json.loads(json_str)
                contents = data.get("contents", {})
                if "twoColumnSearchResultsRenderer" in contents:
                    contents = contents["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
                    for content in contents:
                        item_section = content.get("itemSectionRenderer", {})
                        if "contents" in item_section:
                            for video in item_section["contents"]:
                                res = {}
                                video_data = video.get("videoRenderer", {})
                                res["id"] = video_data.get("videoId", None)
                                res["thumbnails"] = [thumb.get("url", None) for thumb in video_data.get("thumbnail", {}).get("thumbnails", [{}])]
                                res["title"] = video_data.get("title", {}).get("runs", [{}])[0].get("text", None)
                                res["long_desc"] = video_data.get("descriptionSnippet", {}).get("runs", [{}])[0].get("text", None)
                                res["channel"] = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("text", None)
                                res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                                res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
                                res["publish_time"] = video_data.get("publishedTimeText", {}).get("simpleText", 0)
                                res["url_suffix"] = video_data.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", None)
                                results.append(res)
        return results

    def to_dict(self, clear_cache=True):
        result = self.videos
        if clear_cache:
            self.videos = ""
        return result

    def to_json(self, clear_cache=True):
        result = json.dumps({"videos": self.videos})
        if clear_cache:
            self.videos = ""
        return result




