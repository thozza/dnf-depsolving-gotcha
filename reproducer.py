#!/usr/bin/python3

import tempfile
import dnf


def _dnf_base(persistdir):
    base = dnf.Base()
    base.conf.config_file_path = "/dev/null"
    base.conf.module_platform_id = "f34"
    base.conf.persistdir = persistdir
    base.conf.substitutions['arch'] = "x86_64"
    base.conf.substitutions['basearch'] = dnf.rpm.basearch("x86_64")

    repo = dnf.repo.Repo("rpmrepo", base.conf)
    repo.baseurl = "https://rpmrepo.osbuild.org/v2/mirror/public/f34/f34-x86_64-fedora-20210512/"

    base.repos.add(repo)
    base.fill_sack(load_system_repo=False)

    return base


def dnf_depsolve(name, checked_pkg, wanted_pkgs, excluded_pkgs):
    with tempfile.TemporaryDirectory() as persistdir:
        base = _dnf_base(persistdir)
        base.install_specs(wanted_pkgs, exclude=excluded_pkgs)
        base.resolve()

        print("*** Test case '{}' ***".format(name))
        print("checked pkg: {}".format(checked_pkg))
        print("wanted pkg set: {}".format(wanted_pkgs))
        print("excluded pkg set: {}".format(excluded_pkgs))
        print()

        print("Packages in the transaction after depsolve:")
        found = False
        for tsi in base.transaction:
            print(tsi.pkg.name)
            if tsi.pkg.name == checked_pkg:
                found = True

        print()
        if found:
            print("{}: {} IS in the transaction".format(name, checked_pkg))
        else:
            print("{}: {} is NOT in the transaction".format(name, checked_pkg))


def main():
    # test case #1
    dnf_depsolve("only 'zram'", "zram", ["zram"], [])
    
    print()
    
    # test case #2
    dnf_depsolve("'zram' with 'zram-generator' excluded", "zram", ["zram"], ["zram-generator"])

if __name__ == "__main__":
    main()
