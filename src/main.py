import subprocess

if __name__ == '__main__':
    subprocess.run("python sac_dqn_learn.py & python api.py", shell=True)