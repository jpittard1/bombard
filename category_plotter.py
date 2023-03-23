




import glob
import tools


depth_paths = glob.glob(f"{tools.bombard_directory()}results/repeats/d_300/35deg/d_*/depth_results/depth.txt")
depth_paths = [tools.Path(path) for path in depth_paths]

ovito_paths = glob.glob(f"{tools.bombard_directory()}results/repeats/d_300/35deg/d_*/ovito_results/ws_analysis.txt")
ovito_paths = [tools.Path(path) for path in ovito_paths]


for path in ovito_paths:

    file = tools.file_proc(path)

    