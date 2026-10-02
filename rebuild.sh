#!/bin/bash
cd /tmp/build
git clone https://github.com/NeuraVisionLab/neuravisionlab.github.io.git
cd neuravisionlab.github.io
python3 build.py
git add index.html publications.html sitemap.xml robots.txt
git commit -m "Rebuild: Add ACCV and BMVC 2026 publications to homepage and news"
git push https://github.com/NeuraVisionLab/neuravisionlab.github.io.git main
