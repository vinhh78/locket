# dembevinh - Locket Uploader Backend
# Copyright (c) 2026 dembevinh. All rights reserved.

import os
import sys
from flask import Flask, request, jsonify, render_template

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from uploader import LocketUploader, create_locket_client, cleanup_file

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
def login():
    session_path = None
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"success": False, "error": "Vui lòng nhập đầy đủ Email và Mật khẩu"}), 400

        client, session_path = create_locket_client()
        client.login(email, password)

        return jsonify({
            "success": True,
            "token": client.session.id_token,
            "local_id": client.session.uid,
            "email": email
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        cleanup_file(session_path)

@app.route("/api/last-moment", methods=["POST"])
def get_last_moment():
    session_path = None
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        token = data.get("token")
        local_id = data.get("local_id")

        client, session_path = create_locket_client()
        if email and password:
            client.login(email, password)
        elif token:
            client.session.id_token = token
            client.session.uid = local_id

        # Get latest moment
        moments = client.moments.get_latest()
        return jsonify({"success": True, "moment": moments})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        cleanup_file(session_path)

@app.route("/api/upload", methods=["POST"])
def upload_moment():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "Vui lòng chọn ảnh hoặc video để tải lên"}), 400

        file = request.files["file"]
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        token = request.form.get("token", "").strip()
        local_id = request.form.get("local_id", "").strip()
        caption = request.form.get("caption", "").strip()
        media_type = request.form.get("media_type", "image").lower()
        sent_to_all = request.form.get("sent_to_all", "true").lower() in ("true", "1", "yes")

        if not (email and password) and not (token and local_id):
            return jsonify({"success": False, "error": "Bạn chưa đăng nhập hoặc phiên đã hết hạn"}), 401

        file_bytes = file.read()
        if not file_bytes:
            return jsonify({"success": False, "error": "File trống hoặc không hợp lệ"}), 400

        filename = (file.filename or "").lower()
        is_video = media_type == "video" or filename.endswith((".mp4", ".mov", ".m4v", ".webm", ".avi"))

        uploader = LocketUploader(email=email, password=password, token=token, local_id=local_id)

        if is_video:
            result = uploader.post_media(
                video_bytes=file_bytes,
                caption=caption,
                sent_to_all=sent_to_all
            )
            return jsonify({
                "success": True,
                "message": "Đăng Video lên Locket thành công!",
                "thumbnail_url": result["thumbnail_url"],
                "video_url": result.get("video_url"),
                "data": result
            })
        else:
            result = uploader.post_media(
                image_bytes=file_bytes,
                caption=caption,
                sent_to_all=sent_to_all
            )
            return jsonify({
                "success": True,
                "message": "Đăng ảnh lên Locket thành công!",
                "thumbnail_url": result["thumbnail_url"],
                "data": result
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  dembevinh Locket Uploader - Bản quyền dembevinh")
    print(f"  Hỗ trợ CẢ ẢNH & VIDEO (tự động nén & chuẩn hóa)")
    print(f"  Đang chạy tại: http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
