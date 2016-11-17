# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.ssh.insert_key = false
  config.vm.box = "bento/centos-7.2"
  config.vm.hostname = "squid-allergy"
  config.vm.provision :shell do |shell|
    shell.path = "provision/provision.sh"
  end
end
