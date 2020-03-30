#!/bin/bash

log_info() { echo >&2 "Info: $@"; }
log_error() { echo >&2 "Error: $@"; }

TMATE_REPO=${TMATE_REPO:-~/.tmate_repo}
TMATE_KEYS="$TMATE_REPO/keys"
TMATE_GITHUB="https://github.com/tmate-io/tmate-ssh-server.git"
PORT=${PORT:-2200}

rpm -q podman --quiet
[ $? -ne 0 ] && {
  log_info "podman is not installed. Installing.."
  sudo dnf install podman || {
    log_error "Cannot install podman."
    exit 1
  }
}

podman images tmate/tmate-ssh-server | grep -q "tmate/tmate-ssh-server" || {
    log_info "The tmate-ssh-server image is missing. Pulling.."
    podman pull tmate/tmate-ssh-server || {
      log_error "Cannot pull the tmate/tmate-ssh-server image."
      exit 1
    }
}

[ ! -d "$TMATE_KEYS" ] && {
  log_info "ssh keys for tmate server are not generated."
  [ ! -d "$TMATE_REPO" ] && {
    log_info "tmate git repo is missing; Clonning into: $TMATE_REPO"
    git clone "$TMATE_GITHUB" "$TMATE_REPO" || {
      log_error "Cannot clone the tmate git repo."
      exit 1
    }
  }

  log_info "Generating keys for tmate server.."
  pushd "$TMATE_REPO"
  ./create_keys.sh 2>&1 | tee .tmp_log || {
    log_error "Cannot generate keys for tmate server."
    rm -f .tmp_log
    exit 1
  }
  log_info "The keys for tmate have been generated."
  log_info "Generating the tmate.conf for the server in: $PWD/generated_tmate.conf"
  log_info "Modify host and port manually in the generated config file."
  grep "set -g tmate" .tmp_log > generated_tmate.conf || {
    # just seatbelt; not needed for the tmate server anyway
    log_error "default tmate conf has not been generated. Generated it manually."
  }
  rm -f .tmp_log
  popd
}

log_info "Open the port $PORT for tcp publicly."
sudo firewall-cmd --zone=public --add-port=2200/tcp || {
  log_error "Cannot open the port in firewall."
  exit 1
}

log_info "starting the container with tmate server as: tmate_server"

podman run --rm --cap-add=SYS_ADMIN --name tmate_server \
           -e PORT=$PORT -e SSH_PORT_LISTEN=$PORT -p $PORT:$PORT \
           -e SSH_HOSTNAME=$(hostname) --volume "$TMATE_KEYS":/root/keys:Z \
           -e SSH_KEYS_PATH=/root/keys -t tmate-ssh-server /bin/bash &

sleep 2;
podman ps -p | grep -q "tmate_server" || {
  log_error "Something wrong happend. The server is not running."
  exit 1
}

log_info "The server is running. To stop the server run: podman stop tmate_server"

log_info "Do not forget to set the ~/.tmate.conf  :)"
exit 0
