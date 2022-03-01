#!/bin/sh

# Exit on error
set -e

# Force packages database sync
pacman -Syy

# Check if there are any updates to installed packages
if [ $(pacman -Su --print | wc -c) != 0 ]; then
  MSG="<b style='color:#ff9933;font-size:large;>&#x1F6E0 There are updates available &#x1F6E0</b> \
        <br /><br /> \
        $(pacman -Su --print) \
        <br /><br /> \
        Follow the instructions to upgrade:<br /><br /> \
        1. Update plan version to today's date in yyyymmdd format:<br /> \
        <code>vim ~/git/src/github.com/buvis-net/clusters/production/operations/system-upgrade/system-upgrade-controller/plans/archlinux.yaml</code><br /><br />
        2. Apply the plan:<br /> <code>kubectl apply -f ~/git/src/github.com/buvis-net/clusters/production/operations/system-upgrade/system-upgrade-controller/plans/archlinux.yaml</code>
      "
else
  MSG="<b style='color:#2e8b57;font-size:large;'>&#x1F44C There are no updates available &#x1F44C</b>"
fi

# Send the email
echo $MSG | mailx -M "text/html" -s "Archlinux upgrade check" tomas@buvis.net
