# dembevinh - Locket Uploader
# Copyright (c) 2026 dembevinh. All rights reserved.

import tempfile
import os
from locketlam import LocketClient

class LocketUploader:
    def __init__(self, email=None, password=None, token=None, local_id=None):
        self.client = LocketClient(auto_emulate=True)
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
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except Exception:
                    pass
