# Introducing DeepBrew
DeepBrew is an open-source research project which began as an undergraduate thesis topic and has expanded into an area of focus for Deeplink, this repository is a work in progress. DeepBrew is an on-chain implementation of The Beer Game, a famous macroeconomics board game in which four players must optimize a supply chain, exchanging beer for money-our version uses ERC20 tokens on an Ethereum test-network, on which players are represented by addresses, and are given algorithmic behavioural strategies inspired by the popular 'base-stock' policy for The Beer Game. 

In addition to the game environemnt, DeepBrew also includes a soft actor-critic deep Q-learning model tuned to play the game optimally as the distributor agent. We propose that DeepBrew's On-chain Beer Game can serve both as a demonstration of Deeplink's proposed 'Cluster' architecture, and as a standard for evaulating the performance of off-to-on-chain machine learning techniques. We also would like to invite the broader community to try their hand at further optimising and improving the system with their own machine learning and middleware solutions.

Stay tuned for further developments as we migrate the system further on-chain via the implementation of smart contract and keeper pairs in lieu of Web3 wallet transactions, along with an interactive GUI frontend demonstration hosted in IPFS.

# Using DeepBrew Ganache
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
