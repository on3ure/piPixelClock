#!/bin/bash

run() {
  exec=$1
  printf "\x1b[38;5;104m -- ${exec}\x1b[39m\n"
  eval ${exec}
}

rungnomon () {
  exec=$1
  printf "\x1b[38;5;104m -- ${exec}\x1b[39m\n"
  eval ${exec} | gnomon --ignore-blank -h
}

say () {
  say=$1
  printf "\x1b[38;5;220m${say}\x1b[38;5;255m\n"
}

#pip3 install python-telegram-bot

run "useradd -r telegram"
run "useradd -r temp"

cat <<EOF > /etc/systemd/system/telegram.service
[Unit]
Description=telegram service
Wants=network.target
After=network.target
[Service]
Type=simple
Environment=HOME=/opt/piPixelClock
WorkingDirectory=/opt/piPixelClock
User=telegram
Nice=1
TimeoutSec=300
ExecStart=python3 bot.py
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > /etc/systemd/system/clock.service
[Unit]
Description=clock service
Wants=network.target
After=network.target
[Service]
Type=simple
Environment=HOME=/opt/piPixelClock
WorkingDirectory=/opt/piPixelClock
User=root
Nice=1
TimeoutSec=300
ExecStart=python clock.py > /dev/null 2>&1
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > /etc/systemd/system/temp.service
[Unit]
Description=temp service
Wants=network.target
After=network.target
[Service]
Type=simple
Environment=HOME=/opt/piPixelClock
WorkingDirectory=/opt/piPixelClock
User=temp
Nice=1
TimeoutSec=300
ExecStart=python3 temp.py
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF

say "Configure systemd"
run "systemctl daemon-reload"
run "systemctl enable redis"
run "systemctl restart redis"
run "systemctl enable telegram"
run "systemctl restart telegram"
run "systemctl enable temp"
run "systemctl restart temp"
run "systemctl enable clock"
run "systemctl restart clock"
