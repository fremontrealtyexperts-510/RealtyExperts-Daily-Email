const fs = require('fs');
const https = require('https');

// Read admin token from .env
const envContent = fs.readFileSync('.env', 'utf8');
const adminToken = envContent.split('\n').find(line => line.startsWith('ADMIN_TOKEN=')).split('=')[1];

// Read chart HTML from REALTY-EXPERTS-Agent-Hub directory
const chartHTML = fs.readFileSync('/Users/harvinderbalu1/Library/CloudStorage/OneDrive-Personal/ClaudeCode/REALTY-EXPERTS-Agent-Hub/latest_inventory_chart.html', 'utf8');

const supabaseUrl = 'rdxzxokcbmmjjgyevqxq.supabase.co';
const apiKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkeHp4b2tjYm1tampneWV2cXhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwODY4NTEsImV4cCI6MjA4NDY2Mjg1MX0.oiIewgoknkmVCZ4NvU8ElkjrVPoIjT7pBjHCaABVsl4';

const payload = JSON.stringify({
  action: 'UPDATE',
  token: adminToken,
  content_type: 'html_display',
  content: chartHTML
});

const options = {
  hostname: supabaseUrl,
  path: '/functions/v1/glance-api',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload),
    'apikey': apiKey
  }
};

console.log('🚀 Uploading inventory chart to database...');

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log(`Status: ${res.statusCode}`);
    if (res.statusCode === 200) {
      console.log('✅ Successfully uploaded inventory chart!');
      console.log('🎉 Chart is now live at: https://teamrealtyexperts.com/todays-inventory');
    } else {
      console.log('❌ Upload failed');
      console.log('Response:', data);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Error:', error.message);
});

req.write(payload);
req.end();
