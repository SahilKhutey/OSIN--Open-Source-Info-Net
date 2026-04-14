import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { Kafka } from 'kafkajs';

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());

// Kafka Configuration
const kafka = new Kafka({
  clientId: 'osin-xr-bridge',
  brokers: [process.env.KAFKA_BOOTSTRAP_SERVERS || 'kafka:29092']
});

const consumer = kafka.consumer({ groupId: 'xr-bridge-group' });

const startKafka = async () => {
  await consumer.connect();
  await consumer.subscribe({ topics: ['osin.processed.nlp', 'osin.processed.cv', 'osin.intelligence.events'], fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      if (message.value) {
        const data = JSON.parse(message.value.toString());
        // Transform for XR environment if needed
        const xrNode = {
          id: data.original_id || data.id,
          type: data.processed_type === 'nlp_sentiment' ? 'neutral' : 'threat',
          priority: data.intelligence?.score > 0.8 ? 'critical' : 'medium',
          position: data.coordinates || [
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10
          ],
          data: data.intelligence,
          connections: []
        };
        
        io.emit('intelligence_update', xrNode);
      }
    },
  });
};

io.on('connection', (socket) => {
  console.log('XR client connected:', socket.id);
  
  socket.on('xr_gesture', (data) => {
    console.log('Received gesture feedback:', data.gesture);
    // Broadcast for cross-client feedback if needed
    io.emit('gesture_feedback', { ...data, processed: true });
  });

  socket.on('disconnect', () => {
    console.log('XR client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, async () => {
  console.log(`XR Bridge Server (v10) running on port ${PORT}`);
  try {
    await startKafka();
    console.log('Intelligence Stream (Kafka) connected to XR Bridge');
  } catch (err) {
    console.error('Failed to connect to Kafka:', err);
  }
});
