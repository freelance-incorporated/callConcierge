import express from 'express';
import callRoutes from './routes/call.routes.js';

const app = express(); 

app.use(express.json());

app.get('/', (req,res)=> {
    res.send("Server OK");
});

app.use('/calls', callRoutes);

export default app;