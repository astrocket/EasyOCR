# EasyOCR Server

- EasyOCR model serving API.
- Korean, English model included.

Get your gpu cloud -> https://www.paperspace.com/

### install nvidia driver

> install driver scanner
```bash
sudo apt install -y ubuntu-drivers-common
```

> Find your <recommended-driver-name>
```bash
ubuntu-drivers devices
```

> install your driver 
```bash
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
apt-cache search nvidia | grep <recommended-driver-name>
sudo apt-get install <recommended-driver-name>
```

```bash
sudo reboot
```

### install cuda toolkit

```bash
sudo apt update
sudo apt install nvidia-cuda-toolkit
```

```bash
nvcc --version
```

### install docker, docker-compose

> install docker
```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
apt-cache policy docker-ce
sudo apt install docker-ce
sudo systemctl status docker
sudo usermod -aG docker ${USER}
```

> install docker-compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### start serving

> local
```bash
docker-compose -f docker-compose.local.yml up -d
```

> production
```bash
docker-compose up -d
```

#### references

[cuda driver installation](https://linuxconfig.org/how-to-install-cuda-on-ubuntu-20-04-focal-fossa-linux)

[docker installation](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)

[easy ocr training (korean)](https://davelogs.tistory.com/94)