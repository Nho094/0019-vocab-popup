# Vocab Popup

Vocab Popup là một linux app (ứng dụng Python thuần) hiển thị popup thông báo từ vựng tiếng Anh kèm phiên âm IPA và nghĩa tiếng Việt từ file `vocab/tu_vung.txt`. Ứng dụng không yêu cầu cài đặt thêm thư viện ngoài, gửi thông báo qua `notify-send` trên desktop session. File từ vựng sử dụng định dạng TSV ba cột (`english`, `ipa`, `vietnamese`); dòng tiêu đề và dòng trống được bỏ qua, dòng thiếu cột sẽ được cảnh báo ra stderr.

## Sử dụng dòng lệnh trực tiếp

Bạn có thể chạy trực tiếp ứng dụng từ dòng lệnh terminal:

```sh
# Xem hướng dẫn trợ giúp
python3 app.py --help

# Chạy thử một từ ra stdout (không gửi thông báo)
python3 app.py --file vocab/tu_vung.txt --dry-run

# Gửi một thông báo từ vựng rồi thoát ngay lập tức
python3 app.py --file vocab/tu_vung.txt --once

# Chạy lặp lại mặc định mỗi 5 phút (300 giây)
python3 app.py --file vocab/tu_vung.txt

# Chạy lặp lại với khoảng thời gian tùy chỉnh (ví dụ: mỗi 60 giây)
python3 app.py --file vocab/tu_vung.txt --interval 60

# Chạy kiểm thử tự động
python3 -m pytest -q
```

Yêu cầu môi trường: `notify-send` (thuộc gói `libnotify`) có trong `PATH` và desktop session hỗ trợ D-Bus notification service.

## Cấu hình chạy định kỳ bằng systemd timer

Thư mục `systemd/` cung cấp sẵn các file cấu hình unit để định lịch thông báo định kỳ mỗi 5 phút mà không cần tiến trình nền chạy vòng lặp vô tận:
- `systemd/vocab-popup.service`: service kiểu `Type=oneshot` thực thi `app.py --file ... --once`.
- `systemd/vocab-popup.timer`: systemd timer kích hoạt dịch vụ với `OnUnitActiveSec=5min` (mỗi 5 phút).

### Kích hoạt dịch vụ qua systemctl --user

1. Chuẩn bị thư mục ứng dụng và thư mục cấu hình user systemd:
   ```sh
   mkdir -p ~/.local/share/vocab-popup ~/.config/systemd/user
   ```

2. Sao chép mã nguồn (`app.py`, `notifier.py` và thư mục `vocab/`) vào `~/.local/share/vocab-popup/`.

3. Sao chép các unit file vào thư mục cấu hình systemd user:
   ```sh
   cp systemd/vocab-popup.service systemd/vocab-popup.timer ~/.config/systemd/user/
   ```

4. Nạp lại cấu hình và kích hoạt timer bằng lệnh `systemctl`:
   ```sh
   # Kiểm tra tính hợp lệ của unit file
   systemd-analyze --user verify ~/.config/systemd/user/vocab-popup.service ~/.config/systemd/user/vocab-popup.timer

   # Nạp lại daemon cấu hình systemd của user
   systemctl --user daemon-reload

   # Kích hoạt và bật timer chạy ngay
   systemctl --user enable --now vocab-popup.timer
   
   #Thay đổi và khôi phục cấu trúc
   cp systemd/vocab-popup.service systemd/vocab-popup.timer                           ~/.config/systemd/user/
   rm -rf ~/.local/share/vocab-popup/*
   mkdir -p ~/.local/share/vocab-popup/vocab
   cp app.py notifier.py vocab.py ~/.local/share/vocab-popup/
   mkdir -p ~/.local/share/vocab-popup/vocab
   cp vocab/tu_vung.txt vocab/vocab.py ~/.local/share/vocab-popup/vocab/
   ```

### Quản lý và theo dõi bằng systemctl

- Xem trạng thái của systemd timer:
  ```sh
  systemctl --user status vocab-popup.timer
  ```

- Xem danh sách các timer và thời điểm kích hoạt tiếp theo:
  ```sh
  systemctl --user list-timers --all
  ```

- Theo dõi nhật ký log thực thi của service:
  ```sh
  journalctl --user -u vocab-popup.service -f
  ```

- Dừng và vô hiệu hóa timer:
  ```sh
  systemctl --user disable --now vocab-popup.timer
  ```
# Gentoo
## Cài hiển thị thông báo 
sudo emerge -avg mako
# Arch
yay -S mako
