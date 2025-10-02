"""
YouTube Transcript MCP Server using FastMCP

An MCP server that fetches YouTube transcripts with timestamp-based retrieval.
"""

from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
import json

# Initialize FastMCP server
mcp = FastMCP("youtube-transcript-server")

ytt_api = YouTubeTranscriptApi()

def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return the ID if already provided."""
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        if "youtu.be/" in url_or_id:
            return url_or_id.split("youtu.be/")[1].split("?")[0]
        elif "v=" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]
    return url_or_id

@mcp.tool()
def get_youtube_transcript(
    video_url_or_id: str,
    start_time: float = 0,
    end_time: float = None,
    languages: list[str] = None
) -> str:
    """
    Fetches the transcript of a YouTube video between specified timestamps.
    
    Args:
        video_url_or_id: YouTube video URL or video ID
        start_time: Start time in seconds (default: 0)
        end_time: End time in seconds (default: None, means end of video)
        languages: Preferred languages for transcript (default: ['en'])
    
    Returns:
        JSON string containing transcript entries with metadata
    """
    if languages is None:
        languages = ['en']
    
    try:
        # Extract video ID and fetch transcript using the new API
        video_id = extract_video_id(video_url_or_id)
        fetched_transcript = ytt_api.fetch(video_id, languages=languages)
        
        # Calculate total duration from snippets
        total_duration = 0
        if len(fetched_transcript) > 0:
            last_snippet = fetched_transcript[-1]
            total_duration = last_snippet.start + last_snippet.duration
        
        # Set end_time to total duration if not specified
        if end_time is None:
            end_time = total_duration
        
        # Validate timestamps
        if start_time < 0:
            return f"Error: start_time must be >= 0"
        if end_time < start_time:
            return f"Error: end_time ({end_time}s) must be >= start_time ({start_time}s)"
        
        # Filter snippets by timestamp
        filtered_snippets = [
            snippet for snippet in fetched_transcript
            if snippet.start >= start_time and snippet.start < end_time
        ]
        
        # Format the text with timestamps - better for LLM context
        text_content = "\n".join([
            f"[{snippet.start:.2f}s] {snippet.text}"
            for snippet in filtered_snippets
        ])
        
        # Build response with metadata
        result = {
            "video_id": fetched_transcript.video_id,
            "language": fetched_transcript.language,
            "language_code": fetched_transcript.language_code,
            "is_generated": fetched_transcript.is_generated,
            "total_duration": f"{total_duration:.2f}s",
            "requested_start_time": f"{start_time:.2f}s",
            "requested_end_time": f"{end_time:.2f}s",
            "actual_start_time": f"{filtered_snippets[0].start:.2f}s" if filtered_snippets else "N/A",
            "actual_end_time": f"{filtered_snippets[-1].start:.2f}s" if filtered_snippets else "N/A",
            "total_entries": len(fetched_transcript),
            "returned_entries": len(filtered_snippets),
            "transcript": text_content
        }
        
        return json.dumps(result, indent=2)
        
    except TranscriptsDisabled:
        return f"Error: Transcripts are disabled for video: {video_url_or_id}"
    except NoTranscriptFound:
        return f"Error: No transcript found for video: {video_url_or_id} in languages: {languages}"
    except VideoUnavailable:
        return f"Error: Video unavailable: {video_url_or_id}"
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

@mcp.tool()
def get_transcript_info(video_url_or_id: str) -> str:
    """
    Get information about available transcripts for a YouTube video.
    
    Args:
        video_url_or_id: YouTube video URL or video ID
    
    Returns:
        JSON string with available transcript languages, total entries, and video duration
    """
    try:
        video_id = extract_video_id(video_url_or_id)
        transcript_list = ytt_api.list(video_id)
        
        available_transcripts = []
        for transcript in transcript_list:
            transcript_info = {
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable,
            }
            # Add translation languages if available
            if transcript.is_translatable and hasattr(transcript, 'translation_languages'):
                transcript_info["translation_languages"] = [
                    {"language": lang.language, "language_code": lang.language_code}
                    for lang in transcript.translation_languages
                ]
            available_transcripts.append(transcript_info)
        
        # Fetch one transcript to get total entry count and duration
        first_transcript = transcript_list.find_transcript(['en'])
        fetched = first_transcript.fetch()
        total_entries = len(fetched)
        
        # Calculate total duration from snippets
        total_duration = 0
        if len(fetched) > 0:
            last_snippet = fetched[-1]
            total_duration = last_snippet.start + last_snippet.duration

        result = {
            "video_id": video_id,
            "total_entries": total_entries,
            "total_duration": f"{total_duration:.2f}s",
            "total_duration_formatted": format_duration(total_duration),
            "available_transcripts": available_transcripts
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error getting transcript info: {str(e)}"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

if __name__ == "__main__":
    mcp.run()