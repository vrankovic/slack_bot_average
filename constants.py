import pathlib

root_dir = pathlib.Path(__file__).parent.absolute()
path_conf_file = f"{root_dir}/plugins/rtmbot.conf"
print(path_conf_file)