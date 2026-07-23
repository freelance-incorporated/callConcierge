import { Queue } from 'bullmq';
import IOredis from 'ioredis';
import config from './env.js';

const redisConnection = new IOredis(config.redis.url, {
    maxRetriesPerRequest: null //required for BullMQ
});

const taskQueue = new Queue('call-tasks', {
    connection: redisConnection
});

export { taskQueue, redisConnection };