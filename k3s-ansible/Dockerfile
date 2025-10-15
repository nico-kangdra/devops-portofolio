FROM ubuntu:24.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Add Ansible PPA and install Ansible
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository --yes --update ppa:ansible/ansible && \
    apt install -y ansible nano wget unzip && \
    wget https://github.com/k3s-io/k3s-ansible/archive/refs/heads/master.zip && \
    unzip master.zip && mv k3s-ansible-master ansible

WORKDIR /ansible
