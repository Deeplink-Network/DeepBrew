import subprocess

if __name__ == '__main__':
    launch_ngrok = subprocess.Popen(['sudo', 'ngrok', 'http', f'--subdomain=deepbrew', '7777'])
    run_api = subprocess.Popen(["python3", "api.py"]) 
    run_model = subprocess.Popen(["python3", "sac_dqn_learn.py"])
    
    try:
        launch_ngrok
        run_api
        run_model
    except KeyboardInterrupt:
        subprocess.Popen(['sudo', 'pkill', 'python']).wait()