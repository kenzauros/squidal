#!/bin/sh

set -e
set -x
set -i # インタラクティブモード

echo "Start installing..."
yum -y install epel-release
yum -y --enablerepo=epel groupinstall 'Development tools'
yum -y install zlib-devel bzip2 bzip2-devel readline readline-devel sqlite \
sqlite-devel openssl openssl-devel curl-devel expat-devel gettext-devel perl-devel

# Git バージョン取得
git version
version=$(git --version | sed -e 's/^.*\([0-9]\{1,2\}\).*$/\1/')
echo Git major version: $version

# 最新バージョンの git インストール
if [ $version -ge 2 ]; then
  echo "Git is already installed."
else
  echo "Installing Git..."
  cd ~
  curl https://www.kernel.org/pub/software/scm/git/git-2.10.2.tar.gz -o git.tar.gz
  tar zxvf ~/git.tar.gz
  cd ~/git-2.10.2
  make prefix=/usr/local all
  make prefix=/usr/local install
  git --version
  cd ~
  rm -rf ~/git-2.*
  # /usr/local/bin が Vagrant のプロビジョナーでログインしたときに Git が古いままになる
  echo "export PATH=\"/usr/local/bin:\$PATH\"" >> /etc/profile
fi

# pyenv インストール
if which pyenv >/dev/null 2>&1; then
  echo "pyenv is already installed."
else
  git clone https://github.com/yyuu/pyenv.git /opt/pyenv
  echo "export PYENV_ROOT=\"/opt/pyenv\"" >> /etc/profile
  echo "export PATH=\"\$PYENV_ROOT/bin:\$PATH\"" >> /etc/profile
  echo "eval \"\$(pyenv init -)\"" >> /etc/profile
  source /etc/profile
  pyenv install --list
  pyenv install 3.5.2
  python --version
  pyenv rehash
  pyenv global 3.5.2
  python --version
  pyenv versions
fi
