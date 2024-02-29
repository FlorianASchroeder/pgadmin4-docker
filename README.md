[![Pulls](https://img.shields.io/docker/pulls/chinaboeller/pgadmin4.svg?style=flat-square&logo=docker)](https://hub.docker.com/r/chinaboeller/pgadmin4/)
[![DockerBuild](https://img.shields.io/docker/cloud/build/chinaboeller/pgadmin4.svg?style=flat-square&logo=docker)](https://hub.docker.com/r/chinaboeller/pgadmin4/)
[![CircleCI](https://img.shields.io/circleci/project/github/FlorianASchroeder/pgadmin4-docker.svg?style=flat-square&logo=circleci)](https://circleci.com/gh/FlorianASchroeder/pgadmin4-docker)

Last updated by bot: 2024-02-29

# pgAdmin 4

This is a simple Docker image for running pgAdmin 4 in a container. The default
configuration is not intended for production use (it runs in "desktop mode",
so authentication is disabled).

This image uses an unprivileged user, and uses port `5050` instead of `80`.
To access the web-interface on port `80` instead of `5050`, you can map the
port using `-p 80:5050`.

## Tags
To use a specific combination of pgAdmin 4 and python see the following table of available image tags.

| Tag | pgAdmin version | Python version | Distro |
| --- | --- | --- | --- |
| `8.3-py3.12` | 8.3 | 3.12.2 | bullseye |
| `8.3-py3.12-alpine` | 8.3 | 3.12.2 | alpine |
| `8.3-py3.11` | 8.3 | 3.11.8 | bullseye |
| `8.3-py3.11-alpine` | 8.3 | 3.11.8 | alpine |
| `8.3-py3.10` | 8.3 | 3.10.13 | bullseye |
| `8.3-py3.10-alpine` | 8.3 | 3.10.13 | alpine |
| `8.3-py3.9` | 8.3 | 3.9.18 | bullseye |
| `8.3-py3.9-alpine` | 8.3 | 3.9.18 | alpine |
| `8.3-py3.8` | 8.3 | 3.8.18 | bullseye |
| `8.3-py3.8-alpine` | 8.3 | 3.8.18 | alpine |
| `8.2-py3.12` | 8.2 | 3.12.2 | bullseye |
| `8.2-py3.12-alpine` | 8.2 | 3.12.2 | alpine |
| `8.2-py3.11` | 8.2 | 3.11.8 | bullseye |
| `8.2-py3.11-alpine` | 8.2 | 3.11.8 | alpine |
| `8.2-py3.10` | 8.2 | 3.10.13 | bullseye |
| `8.2-py3.10-alpine` | 8.2 | 3.10.13 | alpine |
| `8.2-py3.9` | 8.2 | 3.9.18 | bullseye |
| `8.2-py3.9-alpine` | 8.2 | 3.9.18 | alpine |
| `8.2-py3.8` | 8.2 | 3.8.18 | bullseye |
| `8.2-py3.8-alpine` | 8.2 | 3.8.18 | alpine |
| `8.1-py3.12` | 8.1 | 3.12.2 | bullseye |
| `8.1-py3.12-alpine` | 8.1 | 3.12.2 | alpine |
| `8.1-py3.11` | 8.1 | 3.11.8 | bullseye |
| `8.1-py3.11-alpine` | 8.1 | 3.11.8 | alpine |
| `8.1-py3.10` | 8.1 | 3.10.13 | bullseye |
| `8.1-py3.10-alpine` | 8.1 | 3.10.13 | alpine |
| `8.1-py3.9` | 8.1 | 3.9.18 | bullseye |
| `8.1-py3.9-alpine` | 8.1 | 3.9.18 | alpine |
| `8.1-py3.8` | 8.1 | 3.8.18 | bullseye |
| `8.1-py3.8-alpine` | 8.1 | 3.8.18 | alpine |
| `8.0-py3.12` | 8.0 | 3.12.2 | bullseye |
| `8.0-py3.12-alpine` | 8.0 | 3.12.2 | alpine |
| `8.0-py3.11` | 8.0 | 3.11.8 | bullseye |
| `8.0-py3.11-alpine` | 8.0 | 3.11.8 | alpine |
| `8.0-py3.10` | 8.0 | 3.10.13 | bullseye |
| `8.0-py3.10-alpine` | 8.0 | 3.10.13 | alpine |
| `8.0-py3.9` | 8.0 | 3.9.18 | bullseye |
| `8.0-py3.9-alpine` | 8.0 | 3.9.18 | alpine |
| `8.0-py3.8` | 8.0 | 3.8.18 | bullseye |
| `8.0-py3.8-alpine` | 8.0 | 3.8.18 | alpine |
| `7.8-py3.12` | 7.8 | 3.12.2 | bullseye |
| `7.8-py3.12-alpine` | 7.8 | 3.12.2 | alpine |
| `7.8-py3.11` | 7.8 | 3.11.8 | bullseye |
| `7.8-py3.11-alpine` | 7.8 | 3.11.8 | alpine |
| `7.8-py3.10` | 7.8 | 3.10.13 | bullseye |
| `7.8-py3.10-alpine` | 7.8 | 3.10.13 | alpine |
| `7.8-py3.9` | 7.8 | 3.9.18 | bullseye |
| `7.8-py3.9-alpine` | 7.8 | 3.9.18 | alpine |
| `7.8-py3.8` | 7.8 | 3.8.18 | bullseye |
| `7.8-py3.8-alpine` | 7.8 | 3.8.18 | alpine |
| `6.21-py3.11` | 6.21 | 3.11.8 | bullseye |
| `6.21-py3.11-alpine` | 6.21 | 3.11.8 | alpine |
| `6.21-py3.10` | 6.21 | 3.10.13 | bullseye |
| `6.21-py3.10-alpine` | 6.21 | 3.10.13 | alpine |
| `6.21-py3.9` | 6.21 | 3.9.18 | bullseye |
| `6.21-py3.9-alpine` | 6.21 | 3.9.18 | alpine |
| `6.21-py3.8` | 6.21 | 3.8.18 | bullseye |
| `6.21-py3.8-alpine` | 6.21 | 3.8.18 | alpine |

Lovely! These tags are kept updated automatically (when new minor or patch version are released) by `build_versions.py` which is run twice a day on CircleCI.

## Example use

### Quick start

To see this image in action, run the following command;

```bash
$ docker run --rm -p 5050:5050 thajeztah/pgadmin4
```

This starts a one-off container in non-detached mode, and container logs are
printed in your terminal. After the container has finished starting, visit
`http://[your-docker-host]:5050` in your browser to try pgAdmin 4.

To exit and remove the container, press `CTRL+C` in your terminal.


### Practical example

This example uses a custom network, and runs a PostgreSQL container.

```bash
# create a custom network for easier connecting
$ docker network create pg

# start a postgres container
$ docker run -d -e POSTGRES_PASSWORD=password --network=pg --name postgres postgres:9-alpine

# start pgAdmin container
$ docker run -d -p 5050:5050 --name pgadmin --network=pg thajeztah/pgadmin4
```

Now visit `http://[your-docker-host]:5050` in your browser. You can add the
postgres database (hostname is `postgres`, password is `password`) to test
if everything is working.

![screenshot](https://raw.githubusercontent.com/thaJeztah/pgadmin4-docker/master/pgadmin-screenshot.png)

## Persistent data

Persistent data is stored in a volume, located at `/pgadmin/`. This allows
you to upgrade the container to a new version without losing configuration.

The following directories can be found inside the volume;

- `/pgadmin/config/pgadmin4.db` - SQLite configuration database
- `/pgadmin/storage/` - other storage

You can override the storage location using the `PG_ADMIN_DATA_DIR`
environment variable

## Unprivileged user

pgAdmin runs as an unprivileged user (`pgadmin`) with `uid:gid` `1000:50`.
The `uid:gid` is selected for compatibility with Docker Toolbox, and allows
you to bind-mount a local directory inside the container for persistent
storage

For example, to bind-mount the `/Users/me/pgadmin` directory as storage directory;

```bash
$ docker run -d -p 5050:5050 -v /Users/me/pgadmin:/pgadmin thajeztah/pgadmin4
```

## Run the image with a read-only filesystem

This image can be run with a read-only filesystem. To do so, specify the
`--read-only` flag when starting the container.

```bash
$ docker run -d -p 5050:5050 --name pgadmin --read-only thajeztah/pgadmin4
```

## Runtime configuration

This image can be configured at runtime, by setting environment variables;

- `PG_ADMIN_DATA_DIR` directory to use for storing data (defaults to `/pgadmin/`)
- `PG_ADMIN_PORT` port to listen on (defaults to `5050`)
- `PG_ADMIN_SESSION_DIR` directory to use for storing server-side sessions (defaults to `/dev/shm/pgAdmin4_session`)
- `DEBUG` enable debug mode (detaults to `False`)

More information on pgAdmin 4 development can be found here;

- https://git.postgresql.org/gitweb/?p=pgadmin4.git;a=summary
- https://www.pgadmin.org

## Reporting issues and feature requests

Issues and feature requests can be reported on GitHub;
https://github.com/thaJeztah/pgadmin4-docker
