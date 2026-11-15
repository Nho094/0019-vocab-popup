# Vocab Popup

Ứng dụng Python thuần hiển thị một từ tiếng Anh, phiên âm IPA và nghĩa tiếng Việt từ `vocab/tu_vung.txt`.
Không cần cài package Python. File từ vựng là TSV ba cột; dòng tiêu đề và dòng trống được bỏ qua, dòng thiếu cột
được cảnh báo ra stderr.

## Chạy thử

```sh
python3 app.py --help
python3 app.py --file vocab/tu_vung.txt --dry-run
python3 -m pytest -q
```

`--dry-run` chỉ in một dòng, không gọi `notify-send`. `--once` gửi một thông báo rồi thoát. Mặc định ứng dụng
chạy liên tục, chờ 300 giây giữa các từ. `notify-send` cần có trong PATH và desktop session cần cung cấp D-Bus
notifications; lỗi gửi được in ra stderr.

## Chạy định kỳ bằng systemd user timer

Các unit mẫu nằm trong `systemd/`. Chúng chạy ứng dụng một lần mỗi lượt timer, không chạy daemon lặp song song.
Đặt bản ứng dụng và file từ vựng tại `~/.local/share/vocab-popup/` (giữ nguyên thư mục `vocab/` cùng
`tu_vung.txt`), sau đó cài unit vào tài khoản hiện tại:

```sh
mkdir -p ~/.local/share/vocab-popup ~/.config/systemd/user
# Sao chép app.py, notifier.py và thư mục vocab/ từ thư mục dự án vào ~/.local/share/vocab-popup/.
cp systemd/vocab-popup.service systemd/vocab-popup.timer ~/.config/systemd/user/
systemd-analyze --user verify ~/.config/systemd/user/vocab-popup.service ~/.config/systemd/user/vocab-popup.timer
systemctl --user daemon-reload
systemctl --user enable --now vocab-popup.timer
```

Timer gửi từ đầu tiên khoảng một phút sau khi user manager khởi động; các lần sau cách nhau năm phút. Các lệnh
trên chỉ thao tác unit cấp user. Để kiểm tra, dùng `systemctl --user status vocab-popup.timer` và
`journalctl --user -u vocab-popup.service`; tắt lịch bằng `systemctl --user disable --now vocab-popup.timer`.

Nếu `notify-send` chạy được trong terminal nhưng không hiện thông báo từ timer, kiểm tra môi trường desktop/D-Bus
của user manager và log service. Không cần chạy service bằng root.
