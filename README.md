# ethereumpool-supervisor

## Installing

`sudo pip install requests`

`wget https://raw.githubusercontent.com/JusbeR/ethereumpool-supervisor/master/ethereumpool-supervisor.py`

### systemd
Put this to:

`/etc/systemd/system/miningSupervision.service`
```
[Unit]
Description=Start nanopol supervisor

[Service]

WorkingDirectory=/home/<full_path_to_script_location/
ExecStart=/usr/bin/python /home/<full_path_to_script_location/ethereumpool-supervisor.py -l 0x123456<the ethereum address being watched, that is>
Restart=always

[Install]
WantedBy=multi-user.target
```
`sudo systemctl daemon-reload`

`sudo systemctl start miningSupervision.service`

`sudo systemctl enable miningSupervision.service`

### Check
`cat <full_path_to_script_location>/ethereumpool-supervisor.log`

Should show something like:
```
2017-10-25 11:40:09,369 Supervising account: 0x1234567890acdcabbadeadbeed
2017-10-25 11:40:09,369 Checking hash rate in every 5 minutes
2017-10-25 11:40:09,369 Booting computer if hash rate is below 1
2017-10-25 11:40:09,369 Booting computer after 20 minutes if serious problems are detected and after 60 minutes if unsure problems are detected.
```

## Tests

U R kidding?

## Running

`python ethereumpool-supervisor.py --help`

Must be ran with sudo priviledges 'cos reboot won't work otherwise