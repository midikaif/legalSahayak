import os
import shutil

base = r'c:\Users\dell\Documents\sheriyanPrac\legalSahayak\frontend'
src_dir = os.path.join(base, 'src')
os.makedirs(src_dir, exist_ok=True)

for d in ['services', 'hooks', 'constants', 'types']:
    os.makedirs(os.path.join(src_dir, d), exist_ok=True)

for d in ['components', 'contexts', 'utils']:
    src_path = os.path.join(base, d)
    dest_path = os.path.join(src_dir, d)
    if os.path.exists(src_path):
        shutil.move(src_path, dest_path)

print('Moved frontend folders')
