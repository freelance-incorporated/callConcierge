import config from './env.js';
import { PrismaClient } from '@prisma/client';

const dbClient = new PrismaClient({
    datasources: {
        db: {
            url: config.db.url
        }
    },
    log: config.env === 'development' ? ['query', 'error', 'warn'] : ['error']
});

export default dbClient;