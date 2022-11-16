const MyToken = artifacts.require("DeepBrew");

module.exports = function (deployer) {
    deployer.deploy(MyToken, 1000000)
};