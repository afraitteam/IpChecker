## Support Protocol's 
Protocol | Status
:------------ | :-------------
ping | :heavy_check_mark:
nmap | :heavy_check_mark:
tcpdump | :heavy_check_mark:
telnet | :heavy_check_mark:

## Install

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/afraitteam/IpChecker/main/install.sh)"
```

## Start Service

```sh
sudo systemctl start ipchecker.service
```

## Stop Service

```sh
sudo systemctl stop ipchecker.service
```

## Stop Service

```sh
sudo systemctl status ipchecker.service
```

## Enable Auto Run Service

```sh
sudo systemctl enable ipchecker.service
```

## Disable Auto Run Service

```sh
sudo systemctl disable ipchecker.service
```
