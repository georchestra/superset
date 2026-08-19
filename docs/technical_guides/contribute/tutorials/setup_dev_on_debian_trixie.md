# Setup Superset dev environment on Debian Trixie (default python is 3.13)

Debian Trixie and ulterior come with Python 3.13+. At the time of this tuto, Superset only supports python 3.11, seting up a dev environment using python 3.13 seems quite a challenge.

The trick is, actually, to use python 3.11. We'll use pyenv to install a python 3.11 version and build our virtualenv from there.

This tuto will also assume you're starting with a fresh Debian install, and go through the whole dependencies stuff.

## Install and configure python 3.11 using pyenv
### Install pyenv
```bash
# pyenv
curl -fsSL https://pyenv.run | bash
# pyenv bash setup
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
# pyenv necessary libs to install python 3.11
sudo apt-get install libncurses5 libncurses5-dev libncursesw5 \
                     liblzma-dev \
                     libsqlite3-dev \
                     libbzip3-dev \
                     libffi-dev \
                     libreadline-dev \
                     tk-dev 
```
### Install python 3.11
```bash
pyenv install 3.11.14
```
As usual, we'll rather rely on a virtualenv for the dev setup:

## Create a virtualenv using pyenv and python 3.11
```bash
pyenv versions
pyenv virtualenv 3.11.14 superset-pyenv-3.11
# gets created in ~/.pyenv/versions/3.11.14/envs/superset-pyenv-3.11/
# list virtualenvs with `pyenv virtualenvs`
# activate with `pyenv activate superset-pyenv-3.11`
```

## Install system deps packages for superset
Not sure it's still necessary. 
TODO: Check again on another computer running trixie
```bash
sudo apt install python3-dev python3-setuptools libpq-dev \
                  libmariadb3 libmariadb-dev-compat \
                  libldap2-dev libsasl2-dev
```

## Follow Superset installation procedure 
from https://georchestra-superset.readthedocs.io/en/latest/technical_guides/contribute/dev_setup/#set-sec-headers-in-firefox-dev-mode-superset-only-no-georchestra-instance
```bash
# Install dependencies & superset in dev mode
pip install -r requirements/development.txt
pip install -e .

# Prepare the config folder
mkdir -p config
for f in superset_georchestra_config.py georchestra_custom_roles.json LocalizationFr.py GeorchestraCustomizations.py Overrides.py Preconfig.py; do
  wget -O config/$f https://raw.githubusercontent.com/georchestra/superset/refs/heads/main/config/superset/$f
done
export PYTHONPATH=$PWD/config:$PYTHONPATH
export SUPERSET_CONFIG_PATH="~/dev/geOrchestra/superset-core/config/superset_georchestra_config.py"
export SUPERSET_APP_ROOT="/superset"

```

## Run the app dependencies
```bash
docker compose up -d db redis
```


