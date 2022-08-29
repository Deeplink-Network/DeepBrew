pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DeepBrew is ERC20 {
    constructor(uint256 initialSupply) public ERC20("DeepBrew", "BEER") {
        _mint(msg.sender, initialSupply);
    }
}