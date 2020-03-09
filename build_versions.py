import argparse
import json
import os
import re
from datetime import datetime
from functools import cmp_to_key
from io import BytesIO
from pathlib import Path

import docker
import docker.errors
import requests
import semver

from requests_html import HTMLSession

DOCKER_IMAGE_NAME = "chinaboeller/pgadmin4"
VERSIONS_PATH = Path("versions.json")
DEFAULT_DISTRO = "buster"
DISTROS = ["buster", "stretch", "alpine"]
DEFAULT_DISTROS = ["alpine", "buster", "stretch"]
DISTRO_TEMPLATE = {'buster': 'debian', 'stretch': 'debian', 'alpine': 'alpine'}

todays_date = datetime.utcnow().date().isoformat()


by_semver_key = cmp_to_key(semver.compare)


def _fetch_tags(package):
    # Fetch available docker tags
    result = requests.get(f"https://registry.hub.docker.com/v1/repositories/{package}/tags")
    return [r["name"] for r in result.json()]


def _latest_patch(tags, ver, patch_pattern, distro):
    tags = [tag for tag in tags if tag.startswith(ver) and tag.endswith(f"-{distro}") and patch_pattern.match(tag)]
    return sorted(tags, key=by_semver_key, reverse=True)[0] if tags else ""


def scrape_supported_python_versions():
    """Scrape supported python versions (risky)"""
    versions = []
    version_table_selector = "#status-of-python-branches table"

    r = HTMLSession().get("https://devguide.python.org/")
    version_table = r.html.find(version_table_selector, first=True)
    for ver in version_table.find("tbody tr"):
        branch, _, _, first_release, end_of_life, _ = [v.text for v in ver.find("td")]
        versions.append({"version": branch, "start": first_release, "end": end_of_life})

    return versions


def scrape_supported_pgadmin_versions():
    base_url = "https://www.postgresql.org/ftp/pgadmin/pgadmin4"
    versions = []
    version_table_selector = "#pgContentWrap table"
    detail_table_selector = "#pgFtpContent table"
    r = HTMLSession().get(base_url)
    version_table = r.html.find(version_table_selector, first=True)

    for ver in version_table.find("tr"):
        min_ver, = [v.text for v in ver.find("td")]
        if not min_ver.startswith('v'):  
            continue
        # dig deeper
        r_detail = HTMLSession().get(f'{base_url}/{min_ver}/pip')
        detail_table = r_detail.html.find(detail_table_selector, first=True)
        for row in detail_table.find("tr"):
            file, release_date, file_size = [r.text for r in row.find("td")]
            if not file.endswith('whl'):
                continue
            versions.append({
                "version_str": min_ver,
                "version": min_ver.lstrip('v'),
                "file_whl": file,
                "file_asc": file+'.asc',
                "release_date": release_date,
                "file_size": file_size
            })

    return versions


def decide_python_versions(distros):
    python_patch_re = "|".join([r"^(\d+\.\d+\.\d+-{})$".format(distro) for distro in distros])
    python_wanted_tag_pattern = re.compile(python_patch_re)

    tags = [tag for tag in _fetch_tags("python") if python_wanted_tag_pattern.match(tag)]
    # Skip unreleased and unsupported
    supported_versions = [v for v in scrape_supported_python_versions() if v["start"] <= todays_date <= v["end"]]

    versions = []
    for supported_version in supported_versions:
        ver = supported_version["version"]
        for distro in distros:
            canonical_image = _latest_patch(tags, ver, python_wanted_tag_pattern, distro)
            if not canonical_image:
                print(f"Not good. ver={ver} distro={distro} not in tags, skipping...")
                continue
            canonical_version = canonical_image.replace(f"-{distro}", "")
            versions.append(
                {"canonical_version": canonical_version, "image": canonical_image, "key": ver, "distro": distro,
                 "start_date": supported_version["start"], "end_date": supported_version["end"]}
            )

    return sorted(versions, key=lambda v: by_semver_key(v["canonical_version"]), reverse=True)


def decide_pgadmin_versions():
    supported_versions = scrape_supported_pgadmin_versions()
    
    versions = supported_versions
    return versions


def version_combinations(pgadmin_versions, python_versions):
    versions = []
    for p in python_versions:
        for pg in pgadmin_versions:
            if pg["release_date"] < p["start_date"] or pg["release_date"] > p["end_date"] :
                continue
            if not (pg["version"].startswith("4.1") and (pg["version"] >= "4.17" or (pg["version"] >= "4.16" and p["distro"] == 'alpine'))):
                # for now: save time on outdates images
                continue
            distro = f'-{p["distro"]}' if p["distro"] != DEFAULT_DISTRO else ""
            key = f'{pg["version"]}-py{p["key"]}{distro}'
            versions.append(
                {
                    "key": key,
                    "python": p["key"],
                    "python_canonical": p["canonical_version"],
                    "python_image": p["image"],
                    "pgadmin": pg["version"],
                    "pgadmin_canonical": pg["version"]+".0",
                    "pgadmin_whl": pg["file_whl"],
                    "distro": p["distro"],
                }
            )

    versions = sorted(versions, key=lambda v: DISTROS.index(v["distro"]))
    versions = sorted(versions, key=lambda v: by_semver_key(v["python_canonical"]), reverse=True)
    versions = sorted(versions, key=lambda v: by_semver_key(v["pgadmin_canonical"]), reverse=True)
    return versions


def render_dockerfile(version):
    dockerfile_template = Path(f'template-{DISTRO_TEMPLATE[version["distro"]]}.Dockerfile').read_text()
    replace_pattern = re.compile("%%(.+?)%%")

    replacements = {"now": datetime.utcnow().isoformat()[:-7], **version}

    def repl(matchobj):
        key = matchobj.group(1).lower()
        return replacements[key]

    return replace_pattern.sub(repl, dockerfile_template)


def persist_versions(versions, dry_run=False):
    if dry_run:
        return
    with VERSIONS_PATH.open("w+") as fp:
        json.dump({"versions": versions}, fp, indent=2)


def load_versions():
    with VERSIONS_PATH.open() as fp:
        return json.load(fp)["versions"]


def build_new_or_updated(current_versions, versions, dry_run=False, debug=False):
    # Find new or updated
    current_versions = {ver["key"]: ver for ver in current_versions}
    versions = {ver["key"]: ver for ver in versions}
    new_or_updated = []

    for key, ver in versions.items():
        updated = key in current_versions and ver != current_versions[key]
        new = key not in current_versions
        if new or updated:
            new_or_updated.append(ver)

    if not new_or_updated:
        print("No new or updated versions")
        return

    # Login to docker hub
    docker_client = docker.from_env()
    dockerhub_username = os.getenv("DOCKERHUB_USERNAME")
    try:
        docker_client.login(dockerhub_username, os.getenv("DOCKERHUB_PASSWORD"))
    except docker.errors.APIError:
        print(f"Could not login to docker hub with username:'{dockerhub_username}'.")
        print("Is env var DOCKERHUB_USERNAME and DOCKERHUB_PASSWORD set correctly?")
        exit(1)

    # Build, tag and push images
    for version in new_or_updated:
        dockerfile = render_dockerfile(version)
        # docker build wants bytes
        with BytesIO(dockerfile.encode()) as fileobj:
            # save dockerfile to disk for building from path
            with Path(f"tmp.Dockerfile").open("w") as tmp_file:
                tmp_file.write(fileobj.read().decode("utf-8"))
            
            tag = f"{DOCKER_IMAGE_NAME}:{version['key']}"
            pgadmin_version = version["pgadmin"]
            python_version = version["python_canonical"]
            print(
                f"Building image {version['key']} pgadmin: {pgadmin_version} python: {python_version} ...",
                end="",
                flush=True,
            )
            if not dry_run:
                docker_client.images.build(path=os.getcwd(), dockerfile="tmp.Dockerfile", tag=tag, rm=True, pull=True)
            if debug:
                with Path(f"debug-{version['key']}.Dockerfile").open("w") as debug_file:
                    debug_file.write(fileobj.read().decode("utf-8"))
            print(f" pushing...", flush=True)
            if not dry_run:
                retries = 3
                while retries > 0:
                    try:
                        docker_client.images.push(DOCKER_IMAGE_NAME, version["key"])
                        retries = 0
                    except requests.exceptions.ConnectionError as e:
                        print(e)
                        retries -= 1
                        print(f"Retrying... {retries} retries left")
                        



def update_readme_tags_table(versions, dry_run=False):
    readme_path = Path("README.md")
    with readme_path.open() as fp:
        readme = fp.read()

    headings = ["Tag", "pgAdmin version", "Python version", "Distro"]
    rows = []
    for v in versions:
        rows.append([f"`{v['key']}`", v["pgadmin"], v["python_canonical"], v["distro"]])

    head = f"{' | '.join(headings)}\n{' | '.join(['---' for h in headings])}"
    body = "\n".join([" | ".join(row) for row in rows])
    table = f"{head}\n{body}\n"

    start = "the following table of available image tags.\n"
    end = "\nLovely!"
    sub_pattern = re.compile(f"{start}(.+?){end}", re.MULTILINE | re.DOTALL)

    readme_new = sub_pattern.sub(f"{start}\n{table}{end}", readme)
    if readme != readme_new and not dry_run:
        with readme_path.open("w+") as fp:
            fp.write(readme_new)


def save_latest_dockerfile(pgadmin_versions, distro = DEFAULT_DISTRO, dry_run = False):
    # take template and render Dockerfile for latest version
    
    # take latest python version
    python_version = decide_python_versions([distro])[0]
    # tkae latest pgAdmin version
    pgadmin_version = pgadmin_versions[0]

    versions = version_combinations([pgadmin_version], [python_version])  # should be list of length 1; if invalid combination then length 0

    for version in versions:
        dockerfile = render_dockerfile(version)
        with BytesIO(dockerfile.encode()) as fileobj:
            # save dockerfile to disk for building from path
            with Path(f"Dockerfile").open("w") as tmp_file:
                tmp_file.write(fileobj.read().decode("utf-8"))


def main(distros, dry_run, debug):
    # distros = list(set(distros + [DEFAULT_DISTRO]))
    current_versions = load_versions()
    # Use latest patch version from each minor
    python_versions = decide_python_versions(distros)
    # Use latest minor version from each major
    pgadmin_versions = decide_pgadmin_versions()
    versions = version_combinations(pgadmin_versions, python_versions)

    persist_versions(versions, dry_run)
    update_readme_tags_table(versions, dry_run)

    # Build tag and release docker images
    build_new_or_updated(current_versions, versions, dry_run, debug)
    save_latest_dockerfile(pgadmin_versions)

    # FIXME(perf): Generate a CircleCI config file with a workflow (parallell) and trigger this workflow via the API.
    # Ref: https://circleci.com/docs/2.0/api-job-trigger/
    # Ref: https://discuss.circleci.com/t/run-builds-on-circleci-using-a-local-config-file/17355?source_topic_id=19287


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="🐳 Build pgAdmin4 docker images")
    parser.add_argument(
        "-d",
        "--distros",
        dest="distros",
        nargs="*",
        choices=DISTROS,
        help="Specify which distros to build",
        default=DEFAULT_DISTROS,
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run", help="Skip persisting, README update, and pushing of builds"
    )
    parser.add_argument("--debug", action="store_true", help="Write generated dockerfiles to disk")
    args = vars(parser.parse_args())
    main(**args)