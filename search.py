import argparse
import os

from github import Github, Auth


parser = argparse.ArgumentParser(description="Search for code on GitHub")
parser.add_argument("query")
parser.add_argument("-o", "--output_file")
parser.add_argument("-m", "--max_iters")
args = parser.parse_args()

token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise ValueError("Please set the GITHUB_TOKEN environment variable")
auth = Auth.Token(token)
g = Github(auth=auth)

# https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28
results = g.search_code(args.query)
max_iters = args.max_iters or 1000

print(results.totalCount)

processed = dict()

# Ignore package managers, since I am looking for direct uses of libraries
ignored_repos = set(
    [
        "JetBrains/intellij-community",
        "NixOS/nixpkgs",
        "Homebrew/homebrew-core",
        "spack/spack",
        "void-linux/void-packages",
        "msys2/MINGW-packages",
        "gentoo/gentoo",
        "macports/macports-ports",
        "archlinuxarm/PKGBUILDs",
        "alpinelinux/aports",
        "rust-lang/crates.io-index",
        "pfsense/FreeBSD-ports",
        "JuliaPackaging/Yggdrasil",
        "gentoo-mirror/gentoo",
        "opnsense/ports",
        "freebsd/freebsd-ports-kde",
    ]
)

try:
    # iterate over the subset of results that have at least 50 stars
    iters = 0
    for result in results:
        if result.repository.stargazers_count > 50:
            if result.repository.full_name in processed:
                continue
            line = ",".join(
                [
                    result.repository.full_name,
                    str(result.repository.stargazers_count),
                    result.html_url,
                ]
            )
            print(line)
            processed[result.repository.full_name] = line

        iters += 1
        if iters > max_iters:
            print(f"Reached {max_iters=}")
            break
finally:
    sorted = sorted(
        processed.values(), key=lambda x: int(x.split(",")[1]), reverse=True
    )

    if not args.output_file:
        args.output_file = f"results_{args.query}.csv"

    with open(args.output_file, "w") as f:
        for line in sorted:
            f.write(line + "\n")
