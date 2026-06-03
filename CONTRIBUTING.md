This document gives guidelines and steps for contributing to the sunscreen analysis project

Need Python version 3.8 or higher
Need Git

For environment, use bash and clone the repo. Then, cd into sunscreen_analysis2


cd .. \
python -m venv sunscreen_venv\
source sunscreen_venv/bin/activate (for linux or mac)
use venv/Scripts/activate for Windows

cd sunscreen-analysis2
pip install -r requirements.txt

Project Structure \
src/core/ - image loading, intensity analysis\
src/ui/  - ROI selection, preview\
src/data/ - input images (by subject number) \
outputs/reports/ - CSV files per subject \
outputs/master_analysis/ - final summary and graphs

To run:
python main.py \
Enter subject number (hit enter), draw left ROI, draw right ROI (same size, drag from center), draw control ROI \
Preview and confirm (y/n)

Generate formatted summary: python fix_summary.py \
Generate graphs: python auto_graphs.py

One-liner after ALL subjects are done (ROIs are all selected):\
python update_master.py && python fix_summary.py && python auto_graphs.py