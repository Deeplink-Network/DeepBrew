import subprocess

run_api = subprocess.Popen(["python3", "api.py"]) 
run_model = subprocess.Popen(["python3", "sac_dqn_learn.py"])

if __name__ == '__main__':
    
    try:
        run_api
        run_model
    except KeyboardInterrupt:
        subprocess.Popen(['sudo', 'pkill', 'python']).wait()