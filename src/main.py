import subprocess

if __name__ == '__main__':
    run_api = subprocess.Popen(["python", "api.py"]) 
    run_model = subprocess.Popen(["python", "sac_dqn_learn.py"])
    
    try:
        run_api.wait()
        run_model.wait()
    except KeyboardInterrupt:
        run_api.terminate()
        run_model.terminate()