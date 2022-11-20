exec sudo ngrok http --subdomain=deepbrew 7777 &
exec python3 api.py &
exec python3 sac_dqn_learn.py