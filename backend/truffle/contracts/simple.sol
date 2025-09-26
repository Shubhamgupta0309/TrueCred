// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Simple {
    string public message = "Hello Blockchain!";

    function setMessage(string memory newMessage) public {
        message = newMessage;
    }

    function getMessage() public view returns (string memory) {
        return message;
    }
}

