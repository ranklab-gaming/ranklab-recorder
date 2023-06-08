FROM ghcr.io/ranklab-gaming/ranklab-devcontainer:latest

RUN sudo apt-get update
RUN sudo apt-get upgrade -y

RUN echo "Etc/UTC" | sudo tee /etc/timezone && \
    sudo ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    sudo apt-get update && sudo apt-get install -y tzdata && \
    sudo dpkg-reconfigure --frontend noninteractive tzdata

RUN sudo apt-get install \
  python3-pip \
  xvfb \
  freerdp2-x11 \
  libcurl4-openssl-dev \
  libssl-dev \
  scrot \
  python3-tk \
  python3-dev -y

RUN pip install pip --upgrade
