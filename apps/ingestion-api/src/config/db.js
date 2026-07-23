import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';
import config from './env.js';

const { Pool } = pg;

const pool = new Pool({ connectionString: config.db.url });
const adapter = new PrismaPg(pool);//wrapped raw pool by prisma adapter

const db = new PrismaClient({
    adapter,
    log: config.env === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

export default db;