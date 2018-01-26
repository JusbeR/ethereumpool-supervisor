#/bin/bash

set -eu
wget https://raw.githubusercontent.com/JusbeR/ethereumpool-supervisor/master/ethereumpool-supervisor.py
wget https://raw.githubusercontent.com/JusbeR/ethereumpool-supervisor/master/ethermine.py
wget https://raw.githubusercontent.com/JusbeR/ethereumpool-supervisor/master/nanopool.py
wget https://raw.githubusercontent.com/JusbeR/ethereumpool-supervisor/master/power-supervisor.py
wget https://raw.githubusercontent.com/JusbeR/ethereumpool-supervisor/master/power_reader.py
chmod +x ethereumpool-supervisor.py
chmod +x power-supervisor.py