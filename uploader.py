# dembevinh - Locket Uploader
# Copyright (c) 2026 dembevinh. All rights reserved.

import tempfile
import os
import uuid
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


class LocketUploader:
    def __init__(self, email=None, password=None, token=None, local_id=None):
        self.client, self.session_path = create_locket_client()
        if email and password:
            self.client.login(email, password)
        elif token:
            self.client.session.id_token = token
            self.client.session.uid = local_id

    def post_media(self, image_bytes=None, video_bytes=None, caption="", sent_to_all=True, recipients=None):
        """Posts image or video to Locket using full iOS emulation & auto-compression."""
        temp_video_path = None
        try:
            video_input = None
            if video_bytes:
                # Write to temp file because locketlam/ffmpeg expects file path for video
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
                    tf.write(video_bytes)
                    temp_video_path = tf.name
                video_input = temp_video_path

            res = self.client.moments.post(
                image=image_bytes if not video_bytes else None,
                video=video_input,
                caption=caption,
                recipients=recipients if not sent_to_all else None
            )

            return {
                "success": True,
                "thumbnail_url": res.get("thumbnail_url") or res.get("image_url"),
                "video_url": res.get("video_url"),
                "data": res
            }
        finally:
            cleanup_file(temp_video_path)
            cleanup_file(self.session_path)
