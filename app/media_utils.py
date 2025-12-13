import ffmpeg
import os

def create_video_thumbnail(video_path:str, output_path:str, max_width: int, max_height:int):
    """
    Generates a meaningful thumbnail using FFmpeg's thumbnail filter in Python.
    """
    try:
        (
            ffmpeg
            .input(video_path)
            # Apply the 'thumbnail' filter to find the best frame
            .filter('thumbnail')
            # Apply the 'scale' filter using a simple auto-adjusting strategy
            # For a max-width of 320 and max-height of 240, for example:
            .filter('scale', w=max_width, h=max_height)
            .output(output_path, vframes=1, )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"Meaningful thumbnail created at {output_path}")
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")
