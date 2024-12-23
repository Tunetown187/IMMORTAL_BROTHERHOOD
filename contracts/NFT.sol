// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract NFT is ERC721URIStorage, Pausable, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    
    address contractAddress;
    uint256 public cost = 0.01 ether;
    uint256 public maxSupply = 10000;
    bool public revealed = false;
    string public notRevealedUri;
    string public baseURI;
    
    mapping(address => bool) public whitelisted;
    mapping(address => uint256) public mintedAmount;
    uint256 public maxMintAmount = 5;

    constructor(
        string memory _name,
        string memory _symbol,
        string memory _initBaseURI,
        string memory _initNotRevealedUri
    ) ERC721(_name, _symbol) {
        setBaseURI(_initBaseURI);
        setNotRevealedURI(_initNotRevealedUri);
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return baseURI;
    }

    function mint(uint256 _mintAmount) public payable {
        require(_mintAmount > 0, "Need to mint at least 1 NFT");
        require(_mintAmount <= maxMintAmount, "Max mint amount per session exceeded");
        require(_tokenIds.current() + _mintAmount <= maxSupply, "Max NFT limit exceeded");

        if (msg.sender != owner()) {
            if(whitelisted[msg.sender] != true) {
                require(msg.value >= cost * _mintAmount, "Insufficient funds");
            }
        }

        for (uint256 i = 1; i <= _mintAmount; i++) {
            mintNFT(msg.sender);
        }
    }

    function mintNFT(address recipient) private returns (uint256) {
        _tokenIds.increment();
        uint256 newItemId = _tokenIds.current();
        _safeMint(recipient, newItemId);
        return newItemId;
    }

    function walletOfOwner(address _owner) public view returns (uint256[] memory) {
        uint256 ownerTokenCount = balanceOf(_owner);
        uint256[] memory tokenIds = new uint256[](ownerTokenCount);
        for (uint256 i; i < ownerTokenCount; i++) {
            tokenIds[i] = tokenOfOwnerByIndex(_owner, i);
        }
        return tokenIds;
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");
        
        if(revealed == false) {
            return notRevealedUri;
        }

        string memory currentBaseURI = _baseURI();
        return bytes(currentBaseURI).length > 0
            ? string(abi.encodePacked(currentBaseURI, tokenId.toString(), ".json"))
            : "";
    }

    // Only owner functions
    function reveal() public onlyOwner {
        revealed = true;
    }
    
    function setNftPerAddressLimit(uint256 _limit) public onlyOwner {
        maxMintAmount = _limit;
    }
    
    function setCost(uint256 _newCost) public onlyOwner {
        cost = _newCost;
    }

    function setNotRevealedURI(string memory _notRevealedURI) public onlyOwner {
        notRevealedUri = _notRevealedURI;
    }

    function setBaseURI(string memory _newBaseURI) public onlyOwner {
        baseURI = _newBaseURI;
    }

    function pause() public onlyOwner {
        _pause();
    }

    function unpause() public onlyOwner {
        _unpause();
    }

    function whitelistUser(address _user) public onlyOwner {
        whitelisted[_user] = true;
    }
    
    function removeWhitelistUser(address _user) public onlyOwner {
        whitelisted[_user] = false;
    }

    function withdraw() public payable onlyOwner {
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}("");
        require(success);
    }
}
