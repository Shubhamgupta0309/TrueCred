var simple = artifacts.require("./simple.sol");

module.exports = function(deployer) {
  deployer.deploy(simple);
};