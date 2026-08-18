import { Queue } from 'bullmq';
import redisConnection from '../config/redis.js';

const outboundCallsQueue = new Queue('outbound-calls-queue', {
  connection: redisConnection,
});

/**
 * Enqueue a new call job
 * @param {Object} data Job payload containing callId, phoneNumber, userId, script, metadata
 */
export const enqueueCall = async (data) => {
  return await outboundCallsQueue.add('outbound-call', data, {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: 1000,
    removeOnFail: 5000,
  });
};
