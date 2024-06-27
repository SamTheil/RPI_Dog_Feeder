# Dog_Feeder_V2

## Raspberry Pi Repo Setup

Flash HotSpotOS onto RPI and configure as a headless device

### 1. Install Git
```
sudo apt update
sudo apt install git
```

### 2. Clone Repo
On Github repo main page click code and choose ssh option. Copy SSH url, and in RPI terminal run:
```
git clone <SSH-URL-of-your-repo>
```

## Raspberry Pi Setup
Once repo has been installed on RPI, in the repo root directory run:
```
chmod +x setup.sh
sudo ./setup.sh
```
This will install all enviorment dependencies and start some background process. This may take a long time
