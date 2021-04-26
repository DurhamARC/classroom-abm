#!/bin/bash
set -e

tmp_dir=$(mktemp -d)
echo "cd-ing to temp dir $tmp_dir"
cd $tmp_dir
echo "Downloading..."
curl -i -s -c cookies.txt ${MLWIN_SHARE_URL} > /dev/null
curl -s -o mlnscript.deb -b cookies.txt ${MLWIN_DOWNLOAD_URL}
echo "Downloaded."
ls -lh

echo "Installing..."
sudo dpkg -i mlnscript.deb
echo "Done."

cd -
rm -rf $tmp_dir
