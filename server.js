const express = require('express');
const { MongoClient } = require('mongodb');
const os = require('os');
const path = require('path');

const app = express();
const port = process.env.PORT || 8080;
const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017/emidb';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

let db;
let mongoConnected = false;

async function connectToMongo() {
    try {
        const client = new MongoClient(mongoUrl);
        await client.connect();
        db = client.db();
        mongoConnected = true;
        console.log(`Connected to MongoDB: ${mongoUrl}`);
    } catch (err) {
        console.error('MongoDB connection failed:', err.message);
        mongoConnected = false;
    }
}

// Health check
app.get('/health', (req, res) => {
    if (mongoConnected) {
        res.status(200).json({ status: 'ok', mongo: 'reachable' });
    } else {
        res.status(500).json({ status: 'error', mongo: 'unreachable' });
    }
});

// EMI calculation API
app.post('/api/emi', async (req, res) => {
    try {
        const { principal, rate, months } = req.body;
        
        // Server-side validation
        if (!principal || !rate || !months || principal <= 0 || rate <= 0 || months <= 0) {
            return res.status(400).json({ error: 'All inputs must be positive numbers.' });
        }

        const P = parseFloat(principal);
        const annualRate = parseFloat(rate);
        const n = parseInt(months);
        const r = annualRate / 12 / 100;

        const emi = (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
        const totalPayment = emi * n;
        const totalInterest = totalPayment - P;

        const hostname = os.hostname();
        // IP address nikalne ki koshish (optional)
        const networkInterfaces = os.networkInterfaces();
        let ipAddress = '127.0.0.1';
        for (const interfaceName in networkInterfaces) {
            for (const iface of networkInterfaces[interfaceName]) {
                if (iface.family === 'IPv4' && !iface.internal) {
                    ipAddress = iface.address;
                    break;
                }
            }
        }

        const servedBy = `${hostname} (${ipAddress})`;

        const calculation = {
            principal: P,
            rate: annualRate,
            months: n,
            emi: emi,
            totalPayment: totalPayment,
            totalInterest: totalInterest,
            servedBy: servedBy,
            createdAt: new Date()
        };

        if (db) {
            await db.collection('calculations').insertOne(calculation);
        }

        res.json(calculation);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

// History API
app.get('/api/history', async (req, res) => {
    try {
        if (!db) return res.status(500).json({ error: 'DB not connected' });
        const history = await db.collection('calculations')
            .find()
            .sort({ createdAt: -1 })
            .limit(10)
            .toArray();
        res.json(history);
    } catch (err) {
        res.status(500).json({ error: 'Server error' });
    }
});

// Start server
app.listen(port, '0.0.0.0', async () => {
    await connectToMongo();
    console.log(`EMI Calculator app listening on port ${port}`);
});
