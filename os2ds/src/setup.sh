#!/usr/bin/env bash
set -euo pipefail



failure() {
    echo "$0: installation failed"
}

trap failure ERR

DIR="$(dirname "${BASH_SOURCE[0]}")"
VIRTUALENV="$DIR/python-env"

install_system_dependencies() {
    # System dependencies. These are the packages we need that are not present
    # on a fresh Ubuntu install.
    echo "$0: installing system dependencies"

    sudo -H apt-get update
    sudo -H apt-get -y install --no-install-recommends $(grep -oh '^[^#][[:alnum:].-]*' "$DIR"/requirements/sys-requirements/sys-requirements*.txt)
}

pip=$(which pip)
install_python_environment() {
    # Setup virtualenv, install Python packages necessary to run BibOS Admin.
    echo "$0: installing Python environment and dependencies"

    find "$DIR/../requirements" -name requirements*.txt -print0 | xargs -0 -n1 "$pip" install -r
}

# install_system_dependencies
install_python_environment
