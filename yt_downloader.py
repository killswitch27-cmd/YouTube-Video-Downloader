import subprocess
import sys
import argparse
from pathlib import Path



def check_yt_dlp():
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        print("yt-dlp not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print("yt-dlp installed successfully.\n")


def download_video(url: str, output_dir: str = ".", audio_only: bool = False):
    import yt_dlp

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Format: best video up to 1080p + best audio, merged into mp4
    # Falls back to best available if 1080p isn't available
    format_selector = (
        "bestaudio/best"
        if audio_only
        else "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
    )

    ydl_opts = {
        "format": format_selector,
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,          # Single video only; remove to allow playlists
        "progress_hooks": [progress_hook],
        "postprocessors": [],
    }

    if audio_only:
        ydl_opts["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })

    print(f"Downloading: {url}")
    print(f"Output dir : {output_path.resolve()}")
    print(f"Mode       : {'Audio only (mp3)' if audio_only else 'Video up to 1080p (mp4)'}\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Unknown")
        print(f"\n✓ Done: {title}")


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?%").strip()
        speed   = d.get("_speed_str", "?").strip()
        eta     = d.get("_eta_str", "?").strip()
        print(f"\r  {percent}  speed: {speed}  ETA: {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\r  Processing file...                          ", end="", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos at up to 1080p using yt-dlp."
    )
    parser.add_argument("urls", nargs="+", help="One or more YouTube URLs")
    parser.add_argument(
        "-o", "--output",
        default="downloads",
        help="Output directory (default: ./downloads)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Download audio only as MP3",
    )
    args = parser.parse_args()

    check_yt_dlp()

    for url in args.urls:
        try:
            download_video(url, output_dir=args.output, audio_only=args.audio_only)
        except Exception as e:
            print(f"\n✗ Failed to download {url}: {e}")


if __name__ == "__main__":
    main()