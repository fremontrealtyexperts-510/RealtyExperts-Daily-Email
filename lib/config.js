const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '..');

module.exports = {
  SUPABASE_HOSTNAME: 'hbsodfrxadlfladdgvgy.supabase.co',
  ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM',
  GITHUB_RAW_BASE: 'https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main',
  GITHUB_PAGES_BASE: 'https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email',
  CHART_HTML_PATH: '/Users/harvinderbalu1/Library/CloudStorage/OneDrive-Personal/ClaudeCode/REALTY-EXPERTS-Agent-Hub/latest_inventory_chart.html',
  TEMPLATE_PATH: path.join(PROJECT_ROOT, 'daily-market-template.json'),
  ENV_PATH: path.join(PROJECT_ROOT, '.env'),
};
