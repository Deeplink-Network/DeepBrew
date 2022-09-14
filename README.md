# INSTRUCTIONS
## DEPENDENCIES
### LANGUAGES
* python
* node.js
* solidity
### NPM PACKAGES
* ganache-cli
* truffle
### CONDA PACKAGES
* pytorch
* tensorboard
* gym
* stable-baselines3
* tensorflow
### PIP PACKAGES
* web3
* ethtoken
## RUNNING THE GAME
#### TERMINAL 1
Launch a terminal and start up the ganache testnet using the mnemonic to generate the exact wallets and private keys used in the code, give each agent an arbitrarily large balance.
* ganache-cli -d -m myth like bonus scare over problem client lizard pioneer submit female collect -a 5 -e 10000000 -l 10000000 --db ./ganache_db

#### TERMINAL 2
Deploy the DeepBrew ERC20 contract onto the now running testnet.

* cd truffle
* truffle migrate

Optional: check that the contract was deployed correctly.

* truffle console
* const deepbrew = await DeepBrew.deployed()
* (await deepbrew.totalSupply()).toString()
* (await deepbrew.balanceOf('0xFE41FE950d4835bD539AC24fBaaDED16b2E32922')).toString()