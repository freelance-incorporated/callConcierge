import { Queue } from 'bullmq';
import redisConnection from '../config/redis.js';

const outboundTasksQueue = new Queue('call-tasks', {
  connection: redisConnection,
  prefix: process.env.BULLMQ_PREFIX || 'bull',
});

export const enqueueTask = async (task) => {
  const data = {
    schemaVersion: 1,
    taskId: task.id,
    userPhone: task.userPhone,
    recipientPhone: task.recipientPhone,
    instruction: task.instruction,
  };
  for (const field of ['userName', 'recipientName', 'userData']) {
    if (task[field] != null) data[field] = task[field];
  }
  return await outboundTasksQueue.add('outbound-call', data, {
    jobId: data.taskId,
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: 1000,
    removeOnFail: 5000,
  });
};
