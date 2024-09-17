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

## Restart Service

```sh
sudo systemctl restart ipchecker.service
```

## Enable Auto Run Service

```sh
sudo systemctl enable ipchecker.service
```

## Disable Auto Run Service

```sh
sudo systemctl disable ipchecker.service
```



## Sample `Curl` Request

```curl
curl --location 'http://localhost:5000/check' \
--header 'Content-Type: application/json' \
--data '[
    {
        "pack": "nmap",
        "ip": "62.133.63.185",
        "port": 80
    },
    {
        "pack": "nmap",
        "ip": "62.133.63.185",
        "port": 80
    }
]'
```

## Sample `PHP` Request
```php
<?php
$client = new Client();
$headers = [
  'Content-Type' => 'application/json'
];
$body = '[
  {
    "pack": "nmap",
    "ip": "62.133.63.185",
    "port": 80
  },
  {
    "pack": "nmap",
    "ip": "62.133.63.185",
    "port": 80
  }
]';
$request = new Request('POST', 'http://37.32.25.69:5000/check', $headers, $body);
$res = $client->sendAsync($request)->wait();
echo $res->getBody();

```

