import re
import glob
import os
def delete_header(content):
    s = list(re.finditer("^---$", content, re.MULTILINE))
    assert len(s) == 0 or len(s) == 2
    if len(s) == 2:
        assert s[0].start() == 0
        print(f"remove header len= {s[1].end()}")
        return content[s[1].end():]
    return content

def join_folder(folder, final_fname):
    g1 = glob.glob(os.path.join(folder, "*md"))
    g2 = glob.glob(os.path.join(folder,  "*", "*md"))
    files = list(sorted(g1)) + list(sorted(g2))
    to_join = []
    for f in files:
        content = open(f).read()
        content = delete_header(content)
        content = f"# {os.path.basename(f)}\n\n{content}"
        to_join.append(content)
    rez = "\n\n".join(to_join)
    with open(final_fname, 'w') as f:
        f.write(rez)

for d in glob.glob("original_docs/dev-portal/docs/*"):
    if os.path.isdir(d):
        join_folder(d, f"docs/{os.path.basename(d)}.md")
