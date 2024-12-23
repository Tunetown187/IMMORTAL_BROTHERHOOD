// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface IUniswapV2Router02 {
    function swapExactETHForTokens(
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable returns (uint[] memory amounts);
    
    function swapExactTokensForETH(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    
    function getAmountsOut(uint amountIn, address[] calldata path)
        external
        view
        returns (uint[] memory amounts);
}

interface IUniswapV2Factory {
    function getPair(address tokenA, address tokenB)
        external
        view
        returns (address pair);
}

contract TokenSniper is Ownable, ReentrancyGuard {
    IUniswapV2Router02 public uniswapRouter;
    address public WETH;
    
    uint256 public minLiquidity = 5 ether;
    uint256 public maxSlippage = 200; // 2% = 200
    bool public isActive = true;
    
    mapping(address => bool) public blacklistedTokens;
    
    event TokensBought(address token, uint256 amountETH, uint256 tokensReceived);
    event TokensSold(address token, uint256 tokensAmount, uint256 ethReceived);
    
    constructor(address _router, address _WETH) {
        uniswapRouter = IUniswapV2Router02(_router);
        WETH = _WETH;
    }
    
    receive() external payable {}
    
    function snipe(
        address tokenAddress,
        uint256 amount,
        uint256 minTokens
    ) external payable onlyOwner nonReentrant {
        require(isActive, "Sniping is paused");
        require(!blacklistedTokens[tokenAddress], "Token is blacklisted");
        require(msg.value >= amount, "Insufficient ETH sent");
        
        // Check liquidity
        address[] memory path = new address[](2);
        path[0] = WETH;
        path[1] = tokenAddress;
        
        uint256[] memory amountsOut = uniswapRouter.getAmountsOut(amount, path);
        require(amountsOut[1] >= minTokens, "Insufficient output amount");
        
        // Execute swap
        uint256[] memory amounts = uniswapRouter.swapExactETHForTokens{value: amount}(
            minTokens,
            path,
            address(this),
            block.timestamp + 300
        );
        
        emit TokensBought(tokenAddress, amount, amounts[1]);
    }
    
    function sell(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minETH
    ) external onlyOwner nonReentrant {
        require(isActive, "Selling is paused");
        
        IERC20 token = IERC20(tokenAddress);
        require(token.balanceOf(address(this)) >= tokenAmount, "Insufficient token balance");
        
        // Approve router
        token.approve(address(uniswapRouter), tokenAmount);
        
        // Create path
        address[] memory path = new address[](2);
        path[0] = tokenAddress;
        path[1] = WETH;
        
        // Execute swap
        uint256[] memory amounts = uniswapRouter.swapExactTokensForETH(
            tokenAmount,
            minETH,
            path,
            address(this),
            block.timestamp + 300
        );
        
        emit TokensSold(tokenAddress, tokenAmount, amounts[1]);
    }
    
    // Configuration functions
    function setMinLiquidity(uint256 _minLiquidity) external onlyOwner {
        minLiquidity = _minLiquidity;
    }
    
    function setMaxSlippage(uint256 _maxSlippage) external onlyOwner {
        maxSlippage = _maxSlippage;
    }
    
    function toggleActive() external onlyOwner {
        isActive = !isActive;
    }
    
    function blacklistToken(address token, bool blacklist) external onlyOwner {
        blacklistedTokens[token] = blacklist;
    }
    
    // Emergency functions
    function withdrawETH() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    function withdrawTokens(address token) external onlyOwner {
        IERC20 tokenContract = IERC20(token);
        uint256 balance = tokenContract.balanceOf(address(this));
        require(balance > 0, "No tokens to withdraw");
        tokenContract.transfer(owner(), balance);
    }
    
    // View functions
    function getExpectedTokens(
        address tokenAddress,
        uint256 ethAmount
    ) external view returns (uint256) {
        address[] memory path = new address[](2);
        path[0] = WETH;
        path[1] = tokenAddress;
        
        uint256[] memory amounts = uniswapRouter.getAmountsOut(ethAmount, path);
        return amounts[1];
    }
}
