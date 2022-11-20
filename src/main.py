import subprocess

if __name__ == '__main__':
    run_api = subprocess.Popen(["python3", "api.py"]) 
    run_model = subprocess.Popen(["python3", "sac_dqn_learn.py"])
    
    try:
        run_api
        run_model
    except KeyboardInterrupt:
        subprocess.Popen(['sudo', 'pkill', 'python']).wait()