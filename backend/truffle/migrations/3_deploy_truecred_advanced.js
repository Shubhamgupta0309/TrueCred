const TrueCred = artifacts.require("TrueCred");

module.exports = async function(deployer, network) {
  console.log(`Deploying TrueCred contract to ${network} network...`);

  // Deploy the contract
  await deployer.deploy(TrueCred);

  const instance = await TrueCred.deployed();

  console.log(`TrueCred contract deployed at: ${instance.address}`);

  // For test networks, authorize some test issuers
  if (network === 'goerli' || network === 'sepolia' || network === 'development') {
    console.log('Setting up test issuers...');

    // The deployer is already authorized as an issuer in the constructor
    // You can add additional test issuers here if needed

    console.log('Test setup complete!');
  }

  // Log deployment details
  console.log('Deployment Summary:');
  console.log(`- Network: ${network}`);
  console.log(`- Contract: TrueCred`);
  console.log(`- Address: ${instance.address}`);
  console.log(`- Owner: ${await instance.owner()}`);
};