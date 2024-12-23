const hre = require("hardhat");

async function main() {
  // Deploy NFT Contract
  const NFT = await hre.ethers.getContractFactory("NFT");
  const nft = await NFT.deploy(
    "MyNFT",
    "MNFT",
    "ipfs://YOUR_BASE_URI/",
    "ipfs://YOUR_HIDDEN_URI"
  );
  await nft.deployed();
  console.log("NFT deployed to:", nft.address);

  // Deploy NFT Marketplace
  const NFTMarketplace = await hre.ethers.getContractFactory("NFTMarketplace");
  const nftMarketplace = await NFTMarketplace.deploy();
  await nftMarketplace.deployed();
  console.log("NFTMarketplace deployed to:", nftMarketplace.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
