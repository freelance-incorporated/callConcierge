import Redis from 'ioredis';
import config from './env.js';

const redisConnection = new Redis(config.redis.url, {
  maxRetriesPerRequest: null,
});

redisConnection.on('error', (err) => {
  console.error('Redis connection error:', err);
});

export default redisConnection;
