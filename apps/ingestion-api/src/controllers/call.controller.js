import { enqueueCall } from '../queues/call.producer.js';

export const createCall = async (req, res) => {
  try {
    const { phoneNumber, userId, script, metadata } = req.body;
    
    // Generate a simple unique callId (in production, might use uuid or nanoid)
    const callId = `call_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    const jobData = {
      callId,
      phoneNumber,
      userId: userId || 'anonymous',
      script: script || '',
      metadata: metadata || { source: 'api' },
    };

    const job = await enqueueCall(jobData);

    res.status(202).json({
      message: 'Call enqueued successfully',
      callId,
      jobId: job.id,
    });
  } catch (error) {
    console.error('Error enqueueing call:', error);
    res.status(500).json({ error: 'Failed to enqueue call' });
  }
};
