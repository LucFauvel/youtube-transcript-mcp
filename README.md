# YouTube Transcript MCP Server (FastMCP)

A Model Context Protocol (MCP) server built with FastMCP that fetches YouTube video transcripts with pagination support for handling long videos.

## Features

- Fetch transcripts from YouTube videos using URL or video ID
- Pagination support for long videos
- Multiple language support
- Timestamps for each transcript entry
- Get info about available transcripts
- Built with FastMCP for simplicity and reliability

## Installation

[Install uv](https://docs.astral.sh/uv/getting-started/installation) if you don't have it already, uv is necessary to be able to install the required dependencies in claude's isolated environment.

### Step 1: Clone the Repository

```bash
git clone https://github.com/LucFauvel/youtube-transcript-mcp
cd youtube-transcript-mcp
```

### Step 3: Test the Server

```bash
uv run main.py
```

If it starts without errors, you're ready to configure Claude Desktop!

## Usage

### Running the Server Directly

```bash
uv run main.py
```

### Installing as MCP Server

**For Claude Desktop on macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**For Claude Desktop on Windows**: Edit `%APPDATA%/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/youtube-transcript-mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

**For VSCode**: run the **MCP: Open User Configuration** command and edit the mcp.json

Add this configuration:

```json
{
  "servers": {
    "youtube-transcript": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/youtube-transcript-mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

## Available Tools

### 1. get_youtube_transcript

Fetches the transcript of a YouTube video with pagination support.

**Parameters:**
- `video_url_or_id` (required): YouTube video URL or video ID
- `start_time` (optional, default: 0): Start time in seconds (default: 0)
- `end_time` (optional, default: None, means end of video): End time in seconds
- `languages` (optional, default: ["en"]): Array of preferred language codes

**Example Usage:**
```
Get the transcript of the fist 10 seconds of this video https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

```
Get the Spanish transcript for https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

```
Summarize this video https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 2. get_transcript_info

Get information about available transcripts for a YouTube video.

**Parameters:**
- `video_url_or_id` (required): YouTube video URL or video ID

**Example Usage:**
```
What transcripts are available for https://www.youtube.com/watch?v=dQw4w9WgXcQ?
```

## Response Format

### get_youtube_transcript Response

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "English",
  "language_code": "en",
  "is_generated": false,
  "total_duration": "213.42s",
  "requested_start_time": "30.00s",
  "requested_end_time": "45.00s",
  "actual_start_time": "30.02s",
  "actual_end_time": "44.91s",
  "total_entries": 128,
  "returned_entries": 7,
  "transcript": "[30.02s] We’re no strangers to love\n[31.75s] You know the rules and so do I\n[33.48s] A full commitment’s what I’m thinking of\n[36.02s] You wouldn’t get this from any other guy\n[38.10s] I just wanna tell you how I’m feeling\n[41.00s] Gotta make you understand\n[44.91s] Never gonna give you up"
}
```

### get_transcript_info Response

```json
{
  "video_id": "dQw4w9WgXcQ",
  "total_entries": 128,
  "total_duration": "213.42s",
  "total_duration_formatted": "03:33",
  "available_transcripts": [
    {
      "language": "English",
      "language_code": "en",
      "is_generated": false,
      "is_translatable": true,
      "translation_languages": [
        { "language": "Spanish", "language_code": "es" },
        { "language": "French", "language_code": "fr" },
        { "language": "German", "language_code": "de" },
        { "language": "Japanese", "language_code": "ja" }
      ]
    },
    {
      "language": "English (auto-generated)",
      "language_code": "en",
      "is_generated": true,
      "is_translatable": true,
      "translation_languages": [
        { "language": "Spanish", "language_code": "es" },
        { "language": "French", "language_code": "fr" }
      ]
    }
  ]
}
```

## Error Handling

The server handles common errors gracefully:
- Transcripts disabled for video
- No transcript found in requested languages
- Video unavailable
- Invalid page numbers
- Network errors

## Tips for Long Videos

1. Use `get_transcript_info` first to see total entries and duration
3. Specify timestamps of interesting parts or chapters of the video
4. Ask the LLM to space out and sample different timestamps within the video

**Example workflow:**
```
1. Get transcript info for [video URL]
2. Get the first 5 minutes of transcript
3. Summarize the first 5 minutes
4. Get the last 10 minutes of the transcript and summarize it
```

## Getting the Code

The complete main.py code is provided above. Save it as `main.py` and the dependencies are in the pyproject.toml file.

## Project Structure

```
youtube-transcript-mcp/
├── main.py          # Main FastMCP server implementation
├── pyproject.toml   # UV project file
└── README.md         # This file
```

## Dependencies

- `fastmcp`: FastMCP framework for building MCP servers
- `youtube-transcript-api`: For fetching YouTube transcripts

## Troubleshooting

**Server not appearing in Claude Desktop:**
- Ensure the path in config is absolute, not relative
- Check that Python is in your PATH
- Restart Claude Desktop after config changes
- Check Claude Desktop logs for errors

**Transcript not found:**
- Not all videos have transcripts
- Try using `get_transcript_info` to see available languages
- Some videos may have auto-generated transcripts only

## License

MIT License - feel free to use and modify as needed.
