// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

interface ISwapRouter {
    // Define the interface for ISwapRouter here
}

interface IBancorNetwork {
    // Define the interface for IBancorNetwork here
}

interface IUniswapV2Router02 {
    // Define the interface for IUniswapV2Router02 here
}

contract FlashLoanBot is AccessControl, Pausable {
    using SafeERC20 for IERC20;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    IBancorNetwork private immutable bancorNetwork;
    address private immutable BANCOR_ETH_ADDRESS;
    address private immutable BANCOR_ETHBNT_POOL;
    address private immutable BNT;

    IUniswapV2Router02 private immutable sushiRouter;
    address private immutable INJ;

    ISwapRouter private immutable uniswapRouter;
    address private immutable DAI;

    constructor(
        address _bancorNetwork,
        address _bancorEthAddress,
        address _bancorEthBntPool,
        address _bnt,
        address _sushiRouter,
        address _inj,
        address _uniswapRouter,
        address _dai
    ) {
        bancorNetwork = IBancorNetwork(_bancorNetwork);
        BANCOR_ETH_ADDRESS = _bancorEthAddress;
        BANCOR_ETHBNT_POOL = _bancorEthBntPool;
        BNT = _bnt;
        sushiRouter = IUniswapV2Router02(_sushiRouter);
        INJ = _inj;
        uniswapRouter = ISwapRouter(_uniswapRouter);
        DAI = _dai;

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(ADMIN_ROLE, msg.sender);
        _setupRole(PAUSER_ROLE, msg.sender);

        // Only the admin can grant/revoke the ADMIN_ROLE
        _setRoleAdmin(ADMIN_ROLE, DEFAULT_ADMIN_ROLE);
    }

    function executeFlashLoan(uint256 amount, uint256 amountOutMinBancor, uint256 amountOutMinSushiSwap, uint256 amountOutMinUniswap) external onlyRole(ADMIN_ROLE) whenNotPaused {
        // Perform actions with the flash loaned amount
        // Add your logic here for utilizing the flash loan

        // Example: trade on Bancor
        _tradeOnBancor(amount, amountOutMinBancor);

        // Example: trade on SushiSwap
        _tradeOnSushi(amount, amountOutMinSushiSwap);

        // Example: trade on Uniswap
        _tradeOnUniswap(amount, amountOutMinUniswap);

        // Repay the flash loan
        // Ensure that the contract has enough funds to repay the loan
        // If the contract balance is insufficient, the transaction will fail
        // Make sure to handle this scenario properly
        // It's recommended to perform flash loan actions last in the function
        // to minimize the risk of failures

        // Example: Repay on Bancor
        _tradeOnBancor(amount, 0);

        // Example: Repay on SushiSwap
        _tradeOnSushi(amount, 0);

        // Example: Repay on Uniswap
        _tradeOnUniswap(amount, 0);
    }

    function _tradeOnBancor(uint256 amountIn, uint256 amountOutMin) private {
        bancorNetwork.convertByPath{value: amountIn}(_getPathForBancor(), amountIn, amountOutMin, address(0), address(0), 0);
    }

    function _getPathForBancor() private pure returns (address[] memory) {
        address[] memory path = new address[](3);
        path[0] = BANCOR_ETH_ADDRESS;
        path[1] = BANCOR_ETHBNT_POOL;
        path[2] = BNT;

        return path;
    }

    function _tradeOnSushi(uint256 amountIn, uint256 amountOutMin) private {
        address recipient = address(this);
        uint256 deadline = block.timestamp + 300;

        sushiRouter.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            _getPathForSushiSwap(),
            recipient,
            deadline
        );
    }

    function _getPathForSushiSwap() private pure returns (address[] memory) {
        address[] memory path = new address[](2);
        path[0] = BNT;
        path[1] = INJ;

        return path;
    }

    function _tradeOnUniswap(uint256 amountIn, uint256 amountOutMin, uint24 fee, uint160 sqrtPriceLimitX96) private {
        address tokenIn = INJ;
        address tokenOut = DAI;
        address recipient = msg.sender;
        uint256 deadline = block.timestamp + 300;

        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams(
            tokenIn,
            tokenOut,
            fee,
            recipient,
            deadline,
            amountIn,
            amountOutMin,
            sqrtPriceLimitX96
        );

        uniswapRouter.exactInputSingle(params);
        uniswapRouter.refundETH();

        // refund leftover ETH to user
        (bool success,) = msg.sender.call{ value: address(this).balance }("");
        require(success, "refund failed");
    }

    // meant to be called as view function
    function multiSwapPreview() external view returns (uint256) {
        uint256 daiBalanceUserBeforeTrade = IERC20(DAI).balanceOf(msg.sender);
        uint256 deadline = block.timestamp + 300;

        uint256 amountOutMinBancor = getAmountOutMinBancor();
        uint256 amountOutMinSushiSwap = getAmountOutMinSushiSwap();
        uint256 amountOutMinUniswap = getAmountOutMinUniswap();

        _tradeOnBancor(msg.value, amountOutMinBancor);
        _tradeOnSushi(IERC20(BNT).balanceOf(address(this)), amountOutMinSushiSwap, deadline);
        _tradeOnUniswap(IERC20(INJ).balanceOf(address(this)), amountOutMinUniswap, deadline);

        uint256 daiBalanceUserAfterTrade = IERC20(DAI).balanceOf(msg.sender);
        return daiBalanceUserAfterTrade - daiBalanceUserBeforeTrade;
    }

    function getAmountOutMinBancor() private pure returns (uint256) {
        // return the desired amountOutMin for Bancor
    }

    function getAmountOutMinSushiSwap() private pure returns (uint256) {
        // return the desired amountOutMin for SushiSwap
    }

    function getAmountOutMinUniswap() private pure returns (uint256) {
        // return the desired amountOutMin for Uniswap
    }
}