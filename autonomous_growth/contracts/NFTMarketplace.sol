// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract NFTMarketplace is ReentrancyGuard {
    using Counters for Counters.Counter;
    Counters.Counter private _itemIds;
    Counters.Counter private _itemsSold;

    address payable owner;
    uint256 listingPrice = 0.025 ether;

    struct MarketItem {
        uint256 itemId;
        address nftContract;
        uint256 tokenId;
        address payable seller;
        address payable owner;
        uint256 price;
        bool sold;
        bool isAuction;
        uint256 auctionEndTime;
        address highestBidder;
        uint256 highestBid;
    }

    mapping(uint256 => MarketItem) private idToMarketItem;
    mapping(uint256 => mapping(address => uint256)) private bids;

    event MarketItemCreated(
        uint256 indexed itemId,
        address indexed nftContract,
        uint256 indexed tokenId,
        address seller,
        address owner,
        uint256 price,
        bool sold,
        bool isAuction
    );

    event AuctionCreated(
        uint256 indexed itemId,
        uint256 startingPrice,
        uint256 duration
    );

    event BidPlaced(
        uint256 indexed itemId,
        address indexed bidder,
        uint256 amount
    );

    event AuctionEnded(
        uint256 indexed itemId,
        address winner,
        uint256 amount
    );

    constructor() {
        owner = payable(msg.sender);
    }

    function getListingPrice() public view returns (uint256) {
        return listingPrice;
    }

    function createMarketItem(
        address nftContract,
        uint256 tokenId,
        uint256 price
    ) public payable nonReentrant {
        require(price > 0, "Price must be greater than 0");
        require(msg.value == listingPrice, "Must pay listing price");

        _itemIds.increment();
        uint256 itemId = _itemIds.current();

        idToMarketItem[itemId] = MarketItem(
            itemId,
            nftContract,
            tokenId,
            payable(msg.sender),
            payable(address(0)),
            price,
            false,
            false,
            0,
            address(0),
            0
        );

        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);

        emit MarketItemCreated(
            itemId,
            nftContract,
            tokenId,
            msg.sender,
            address(0),
            price,
            false,
            false
        );
    }

    function createAuction(
        address nftContract,
        uint256 tokenId,
        uint256 startingPrice,
        uint256 duration
    ) public payable nonReentrant {
        require(startingPrice > 0, "Starting price must be greater than 0");
        require(msg.value == listingPrice, "Must pay listing price");
        require(duration > 0, "Duration must be greater than 0");

        _itemIds.increment();
        uint256 itemId = _itemIds.current();

        idToMarketItem[itemId] = MarketItem(
            itemId,
            nftContract,
            tokenId,
            payable(msg.sender),
            payable(address(0)),
            startingPrice,
            false,
            true,
            block.timestamp + duration,
            address(0),
            0
        );

        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);

        emit AuctionCreated(itemId, startingPrice, duration);
    }

    function placeBid(uint256 itemId) public payable nonReentrant {
        MarketItem storage item = idToMarketItem[itemId];
        require(item.isAuction, "Not an auction");
        require(block.timestamp < item.auctionEndTime, "Auction ended");
        require(msg.value > item.highestBid, "Bid not high enough");

        if (item.highestBidder != address(0)) {
            // Refund previous highest bidder
            bids[itemId][item.highestBidder] += item.highestBid;
        }

        item.highestBidder = msg.sender;
        item.highestBid = msg.value;

        emit BidPlaced(itemId, msg.sender, msg.value);
    }

    function endAuction(uint256 itemId) public nonReentrant {
        MarketItem storage item = idToMarketItem[itemId];
        require(item.isAuction, "Not an auction");
        require(block.timestamp >= item.auctionEndTime, "Auction not ended");
        require(!item.sold, "Auction already ended");

        item.sold = true;
        item.owner = payable(item.highestBidder);

        if (item.highestBidder != address(0)) {
            item.seller.transfer(item.highestBid);
            IERC721(item.nftContract).transferFrom(address(this), item.highestBidder, item.tokenId);
        } else {
            IERC721(item.nftContract).transferFrom(address(this), item.seller, item.tokenId);
        }

        _itemsSold.increment();

        emit AuctionEnded(itemId, item.highestBidder, item.highestBid);
    }

    function createMarketSale(
        address nftContract,
        uint256 itemId
    ) public payable nonReentrant {
        uint256 price = idToMarketItem[itemId].price;
        uint256 tokenId = idToMarketItem[itemId].tokenId;
        require(msg.value == price, "Please submit asking price");

        idToMarketItem[itemId].seller.transfer(msg.value);
        IERC721(nftContract).transferFrom(address(this), msg.sender, tokenId);
        idToMarketItem[itemId].owner = payable(msg.sender);
        idToMarketItem[itemId].sold = true;
        _itemsSold.increment();
        payable(owner).transfer(listingPrice);
    }

    function fetchMarketItems() public view returns (MarketItem[] memory) {
        uint256 itemCount = _itemIds.current();
        uint256 unsoldItemCount = _itemIds.current() - _itemsSold.current();
        uint256 currentIndex = 0;

        MarketItem[] memory items = new MarketItem[](unsoldItemCount);
        for (uint256 i = 0; i < itemCount; i++) {
            if (idToMarketItem[i + 1].owner == address(0)) {
                uint256 currentId = i + 1;
                MarketItem storage currentItem = idToMarketItem[currentId];
                items[currentIndex] = currentItem;
                currentIndex += 1;
            }
        }
        return items;
    }

    function fetchMyNFTs() public view returns (MarketItem[] memory) {
        uint256 totalItemCount = _itemIds.current();
        uint256 itemCount = 0;
        uint256 currentIndex = 0;

        for (uint256 i = 0; i < totalItemCount; i++) {
            if (idToMarketItem[i + 1].owner == msg.sender) {
                itemCount += 1;
            }
        }

        MarketItem[] memory items = new MarketItem[](itemCount);
        for (uint256 i = 0; i < totalItemCount; i++) {
            if (idToMarketItem[i + 1].owner == msg.sender) {
                uint256 currentId = i + 1;
                MarketItem storage currentItem = idToMarketItem[currentId];
                items[currentIndex] = currentItem;
                currentIndex += 1;
            }
        }
        return items;
    }

    function withdrawBid(uint256 itemId) public nonReentrant {
        uint256 amount = bids[itemId][msg.sender];
        require(amount > 0, "No bid to withdraw");
        
        bids[itemId][msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }

    function updateListingPrice(uint256 _listingPrice) public payable {
        require(owner == msg.sender, "Only marketplace owner");
        listingPrice = _listingPrice;
    }
}
