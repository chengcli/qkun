import os
from qkun.granule import save_to_yaml, load_from_yaml
from qkun.pace import OceanColor
from qkun import CACHE_FOLDER_PATH

basename = "PACE_OCI.20250326T103301.L1B.V3"
digest_path = os.path.join(CACHE_FOLDER_PATH, f"{basename}.global.yaml")

# create an instance of OceanColor
obs = OceanColor(digest_path, verbose=True)

# print the instance
print(obs)

# create auxiliary files such as footprint and field of view
obs.process()

# you can save the instance to a YAML file
save_to_yaml(obs, f"{basename}.yaml")

# or load it back
obs2 = load_from_yaml(f"{basename}.yaml")

# they should be the same
print(obs2)
