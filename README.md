# Dog_Feeder_V2

## Raspberry Pi Repo Setup (Private Repo)

Flash Raspbian onto RPI and configure as a headless device

### 1. Install Git
```
sudo apt update
sudo apt install git
```
### 2. Generate and add SSH key pair on RPI
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```
### 3. Add SSH public key to github account
Display public key on RPI and copy it to clipboard
```
cat ~/.ssh/id_rsa.pub
```
Go to Github account, select "SSH and GPG keys”
Click on “New SSH key”, paste your key into the field, give it a meaningful title, and click “Add SSH key”.

### 4. Clone Repo
On Github repo main page click code and choose ssh option. Copy SSH url, and in RPI terminal run:
```
git clone <SSH-URL-of-your-repo>
```

## Raspberry Pi Airbrake Setup
Once repo has been installed on RPI, in the repo root directory run:
```
chmod +x setup.sh
sudo ./setup.sh
```
This will install all enviorment dependencies and start some background process. This may take a long time
