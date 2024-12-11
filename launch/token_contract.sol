// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract ImmortalToken is ERC20, Ownable, ReentrancyGuard {
    // Token parameters
    uint256 public constant INITIAL_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;
    
    // Tax settings
    uint256 public buyTax = 5; // 5% buy tax
    uint256 public sellTax = 5; // 5% sell tax
    
    // Marketing and development wallets
    address public marketingWallet;
    address public developmentWallet;
    
    // Anti-bot measures
    mapping(address => bool) public isBlacklisted;
    uint256 public maxTransactionAmount;
    uint256 public maxWalletAmount;
    
    // Trading control
    bool public tradingEnabled;
    mapping(address => bool) public isExcludedFromLimits;
    
    constructor() ERC20("Immortal Brotherhood", "IMBT") {
        _mint(msg.sender, INITIAL_SUPPLY);
        maxTransactionAmount = INITIAL_SUPPLY / 100; // 1% max transaction
        maxWalletAmount = INITIAL_SUPPLY / 50;    // 2% max wallet
        
        // Set initial wallets
        marketingWallet = msg.sender;
        developmentWallet = msg.sender;
        
        // Exclude owner from limits
        isExcludedFromLimits[msg.sender] = true;
    }
    
    // Enable trading
    function enableTrading() external onlyOwner {
        tradingEnabled = true;
    }
    
    // Set tax rates
    function setTaxes(uint256 _buyTax, uint256 _sellTax) external onlyOwner {
        require(_buyTax <= 10 && _sellTax <= 10, "Tax cannot exceed 10%");
        buyTax = _buyTax;
        sellTax = _sellTax;
    }
    
    // Override transfer function to implement taxes and limits
    function _transfer(
        address sender,
        address recipient,
        uint256 amount
    ) internal virtual override {
        require(!isBlacklisted[sender] && !isBlacklisted[recipient], "Blacklisted");
        require(tradingEnabled || isExcludedFromLimits[sender], "Trading not enabled");
        
        // Check transaction limits
        if (!isExcludedFromLimits[sender] && !isExcludedFromLimits[recipient]) {
            require(amount <= maxTransactionAmount, "Exceeds max transaction");
            require(balanceOf(recipient) + amount <= maxWalletAmount, "Exceeds max wallet");
        }
        
        // Calculate and apply taxes
        uint256 taxAmount = 0;
        if (!isExcludedFromLimits[sender] && !isExcludedFromLimits[recipient]) {
            taxAmount = (amount * buyTax) / 100;
            if (taxAmount > 0) {
                super._transfer(sender, marketingWallet, taxAmount / 2);
                super._transfer(sender, developmentWallet, taxAmount / 2);
            }
        }
        
        // Transfer remaining amount
        super._transfer(sender, recipient, amount - taxAmount);
    }
    
    // Blacklist/Whitelist functions
    function setBlacklist(address account, bool blacklisted) external onlyOwner {
        isBlacklisted[account] = blacklisted;
    }
    
    // Exclude/Include from limits
    function setExcludedFromLimits(address account, bool excluded) external onlyOwner {
        isExcludedFromLimits[account] = excluded;
    }
    
    // Update wallet addresses
    function updateWallets(address _marketingWallet, address _developmentWallet) external onlyOwner {
        marketingWallet = _marketingWallet;
        developmentWallet = _developmentWallet;
    }
    
    // Emergency token recovery
    function recoverToken(address tokenAddress) external onlyOwner {
        uint256 balance = IERC20(tokenAddress).balanceOf(address(this));
        IERC20(tokenAddress).transfer(owner(), balance);
    }
}
