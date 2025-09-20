import React, { useState, useEffect } from "react";
import Web3 from "web3";
import SimpleContract from "./contracts/Simple.json";

function App() {
  const [account, setAccount] = useState("");
  const [contract, setContract] = useState(null);
  const [message, setMessage] = useState("");
  const [newMessage, setNewMessage] = useState("");

  useEffect(() => {
    const loadWeb3AndContract = async () => {
      if (window.ethereum) {
        try {
          const web3 = new Web3(window.ethereum);
          await window.ethereum.request({ method: "eth_requestAccounts" });

          const accounts = await web3.eth.getAccounts();
          setAccount(accounts[0]);

          const networkId = await web3.eth.net.getId();
          console.log("Connected network ID:", networkId);

          const deployedNetwork = SimpleContract.networks[networkId];
          if (!deployedNetwork) {
            alert(
              `Contract not deployed on this network (ID: ${networkId}). Try migrating again.`
            );
            return;
          }

          const instance = new web3.eth.Contract(
            SimpleContract.abi,
            deployedNetwork.address
          );
          setContract(instance);

          // Load initial message
          const currentMessage = await instance.methods.getMessage().call();
          setMessage(currentMessage);
        } catch (err) {
          console.error("Error loading Web3 or contract:", err);
        }
      } else {
        alert("Please install MetaMask!");
      }
    };

    loadWeb3AndContract();
  }, []);

  const updateMessage = async () => {
    if (!contract) {
      alert("Contract not loaded yet!");
      return;
    }
    if (!newMessage) {
      alert("Please enter a message!");
      return;
    }

    try {
      await contract.methods.setMessage(newMessage).send({ from: account });
      const updatedMessage = await contract.methods.getMessage().call();
      setMessage(updatedMessage);
      setNewMessage("");
    } catch (err) {
      console.error(err);
      alert("Error updating message: " + err.message);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Simple Contract DApp Test</h2>
      <p>
        <strong>Connected account:</strong> {account || "Not connected"}
      </p>
      <p>
        <strong>Current message:</strong> {message}
      </p>

      <input
        type="text"
        placeholder="New message"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        style={{ marginRight: 10 }}
      />
      <button onClick={updateMessage}>Update Message</button>
    </div>
  );
}

export default App;
