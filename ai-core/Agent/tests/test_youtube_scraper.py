from __future__ import annotations

import unittest
from datetime import UTC, datetime

from app.scrapers.youtube import (
    YouTubeChannel,
    build_channel_rss_url,
    extract_channel_id_from_channel_page,
    extract_channel_id_from_rss_url,
    extract_rss_url_from_channel_page,
    filter_videos_by_time,
    parse_channel_feed,
)


SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
      xmlns="http://www.w3.org/2005/Atom">
  <title>Example Channel</title>
  <yt:channelId>UC1234567890123456789012</yt:channelId>
  <entry>
    <yt:videoId>abc123XYZ90</yt:videoId>
    <title>Fresh AI Video</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=abc123XYZ90"/>
    <published>2026-06-11T00:00:00+00:00</published>
    <updated>2026-06-11T00:10:00+00:00</updated>
    <media:group xmlns:media="http://search.yahoo.com/mrss/">
      <media:description>A short AI update.</media:description>
    </media:group>
  </entry>
  <entry>
    <yt:videoId>old123XYZ90</yt:videoId>
    <title>Old AI Video</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=old123XYZ90"/>
    <published>2026-06-09T00:00:00+00:00</published>
    <updated>2026-06-09T00:10:00+00:00</updated>
  </entry>
</feed>
"""


class YouTubeScraperTests(unittest.TestCase):
    def test_channel_url_input_is_valid(self) -> None:
        channel = YouTubeChannel.from_dict(
            {
                "name": "Brady Your Tutor",
                "channel_url": "https://www.youtube.com/@BradyYourTutor",
            }
        )

        self.assertEqual(channel.channel_url, "https://www.youtube.com/@BradyYourTutor")

    def test_build_channel_rss_url(self) -> None:
        url = build_channel_rss_url("UC1234567890123456789012")

        self.assertEqual(
            url,
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012",
        )

    def test_extract_rss_url_from_channel_page(self) -> None:
        html = (
            '<html><head><link rel="alternate" type="application/rss+xml" '
            'href="https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012">'
            "</head></html>"
        )

        self.assertEqual(
            extract_rss_url_from_channel_page(html),
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012",
        )

    def test_extract_channel_id_from_channel_page(self) -> None:
        html = '<script>{"channelId":"UC1234567890123456789012"}</script>'

        self.assertEqual(
            extract_channel_id_from_channel_page(html),
            "UC1234567890123456789012",
        )

    def test_extract_channel_id_from_rss_url(self) -> None:
        self.assertEqual(
            extract_channel_id_from_rss_url(
                "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
            ),
            "UC1234567890123456789012",
        )

    def test_parse_channel_feed(self) -> None:
        channel = YouTubeChannel(name="Example", channel_id="UC1234567890123456789012")

        videos = parse_channel_feed(SAMPLE_FEED, channel)

        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0].video_id, "abc123XYZ90")
        self.assertEqual(videos[0].title, "Fresh AI Video")
        self.assertEqual(videos[0].published_at, datetime(2026, 6, 11, 0, 0, tzinfo=UTC))

    def test_filter_videos_by_time(self) -> None:
        channel = YouTubeChannel(name="Example", channel_id="UC1234567890123456789012")
        videos = parse_channel_feed(SAMPLE_FEED, channel)

        recent = filter_videos_by_time(
            videos,
            since=datetime(2026, 6, 10, 0, 0, tzinfo=UTC),
            until=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
        )

        self.assertEqual([video.video_id for video in recent], ["abc123XYZ90"])


if __name__ == "__main__":
    unittest.main()
