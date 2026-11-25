// Production PM2 Ecosystem Configuration Template
module.exports = {
  apps: [
    {
      name: 'api-service',
      script: 'server.js',
      instances: 1,
      autorestart: true,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'python-worker',
      script: 'worker.py',
      interpreter: 'python3',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      max_memory_restart: '400M',
      time: true
    }
  ]
};
