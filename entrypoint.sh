#!/bin/bash
export HOME=/pgadmin
if ! whoami &> /dev/null; then
    if [ -w /etc/passwd ]; then
        # Required for running in OpenShift
        echo "${USER_NAME:-pga}:x:$(id -u):0:${USER_NAME:-pga} user:${HOME}:/bin/bash" >> /etc/passwd
    fi
fi

exec $@