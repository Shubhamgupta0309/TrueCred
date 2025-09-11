/**
 * Frontend Registration Test Script
 * This script tests the frontend registration API call directly
 */
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

async function testRegistration(userData) {
  try {
    console.log(`Testing registration with data:`, userData);
    
    const response = await axios.post(`${API_URL}/auth/register`, userData, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Registration successful!');
    console.log('Response status:', response.status);
    console.log('Response data:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    console.error('Registration failed!');
    console.error('Error status:', error.response?.status);
    console.error('Error data:', JSON.stringify(error.response?.data, null, 2));
    console.error('Error message:', error.message);
    return false;
  }
}

// Generate a random test user
const randomSuffix = Math.floor(1000 + Math.random() * 9000);
const testUser = {
  email: `college@tcet.com`,
  password: 'College@1234',
  name: `College`,
  username: `College${randomSuffix}`,
  role: 'college'
};

// Run the test
testRegistration(testUser);
