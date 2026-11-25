# dembevinh - Locket Uploader
# Copyright (c) 2026 dembevinh. All rights reserved.

import tempfile
import os
import subprocess
import uuid
import imageio_ffmpeg
from locketlam import LocketClient


def create_locket_client():
    """Create a LocketClient using an isolated writable temp session path."""
    session_path = os.path.join(tempfile.gettempdir(), f"locket_session_{uuid.uuid4().hex}.json")
    return LocketClient(session_path=session_path, auto_emulate=True), session_path


def cleanup_file(path):
    """Remove a temporary file if it exists."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass


def compress_video_low_mem(input_path):
    """Pre-compress video with single-thread ultrafast ffmpeg to fit Render 512MB RAM."""
    if os.path.getsize(input_path) < 5 * 1024 * 1024:
        return input_path, False

    output_path = os.path.join(tempfile.gettempdir(), f"locket_cmp_{uuid.uuid4().hex}.mp4")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-threads", "1",
        "-i", input_path,
        "-t", "30",
        "-vf", "scale='min(720,iw)':-2",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return output_path, True
    cleanup_file(output_path)
    return input_path, False


class LocketUploader:
    def __init__(self, email=None, password=None, token=None, local_id=None):
        self.client, self.session_path = create_locket_client()
        if email and password:
            self.client.login(email, password)
        elif token:
            self.client.session.id_token = token
            self.client.session.uid = local_id

    def post_media(self, image_bytes=None, video_bytes=None, caption="", sent_to_all=True, recipients=None):
        """Posts image or video to Locket using full iOS emulation & low-memory compression."""
        temp_video_path = None
        compressed_video_path = None
        try:
            video_input = None
            auto_compress = True
            if video_bytes:
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
                    tf.write(video_bytes)
                    temp_video_path = tf.name
                video_input, was_compressed = compress_video_low_mem(temp_video_path)
                if was_compressed:
                    compressed_video_path = video_input
                    if os.path.getsize(compressed_video_path) < 6 * 1024 * 1024:
                        auto_compress = False

            res = self.client.moments.post(
                image=image_bytes if not video_bytes else None,
                video=video_input,
                caption=caption,
                recipients=recipients if not sent_to_all else None,
                auto_compress=auto_compress
            )

            return {
                "success": True,
                "thumbnail_url": res.get("thumbnail_url") or res.get("image_url"),
                "video_url": res.get("video_url"),
                "data": res
            }
        finally:
            cleanup_file(temp_video_path)
            cleanup_file(compressed_video_path)
            cleanup_file(self.session_path)
