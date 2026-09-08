import { Queue } from 'bullmq';
import redisConnection from '../config/redis.js';

const outboundTasksQueue = new Queue('call-tasks', {
  connection: redisConnection,
});

/**
 * Enqueue a new task job
 * @param {Object} data Job payload
 */
export const enqueueTask = async (data) => {
  return await outboundTasksQueue.add('outbound-call', data, {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: 1000,
    removeOnFail: 5000,
  });
};
