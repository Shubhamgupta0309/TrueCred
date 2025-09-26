var TrueCred = artifacts.require("./TrueCred.sol");

module.exports = function(deployer) {
  deployer.deploy(TrueCred);
};