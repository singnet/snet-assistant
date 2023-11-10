from openai import OpenAI
import os, glob
import pickle

client = OpenAI()
files = list(glob.glob("docs/*md"))
oi_files = [client.files.create(file=open(f, "rb"), purpose='assistants') for f in files]
all_ids = [f.id for f in oi_files]
pickle.dump(all_ids, open( "all_ids.p", "wb" ) )
