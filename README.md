# dembevinh — Locket Uploader

Ứng dụng web tải Ảnh và Video (lên tới 30 giây) lên Locket Camera không cần tài khoản Locket Gold.

Bản quyền © 2026 **dembevinh**. All rights reserved.

---

## Tính năng

- Đăng nhập trực tiếp tài khoản Locket thông qua Firebase Auth.
- Hỗ trợ tải cả **Hình ảnh** (JPG, PNG, WEBP) và **Video** (MP4, MOV lên tới 30s).
- Tự động nén và chuẩn hóa bằng FFmpeg / Pillow.
- Giao diện tối giản với Viewfinder 1:1 Widget.
- Triển khai sẵn sàng cho cả **Localhost** và **Vercel Serverless**.

---

## Cách chạy trên máy tính cá nhân (Localhost)

```bash
# 1. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 2. Khởi động server
python app.py
```

Truy cập: `http://localhost:5000`

---

## Triển khai lên Vercel

Dự án đã được cấu hình sẵn file `vercel.json` và entrypoint `api/index.py`. Chỉ cần kết nối repository này với [Vercel](https://vercel.com) để deploy tự động hoàn toàn miễn phí.
