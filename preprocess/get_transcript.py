import json
from youtube_transcript_api import YouTubeTranscriptApi as yt


video_id = "nMTJPqx2XBE"
transcript = yt.get_transcript(video_id)
transcript = json.dumps(transcript[0])
print(type(transcript))


