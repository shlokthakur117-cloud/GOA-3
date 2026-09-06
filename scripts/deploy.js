import hre from "hardhat";

async function main() {
  const VerificationRegistry = await hre.ethers.getContractFactory("VerificationRegistry");
  const registry = await VerificationRegistry.deploy();

  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log(`VerificationRegistry deployed to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
