import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import cors from 'cors';

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

app.use(cors());

interface User {
  id: string;
  position: [number, number, number];
  rotation: [number, number, number];
  avatar: string;
  name: string;
}

const users: Record<string, User> = {};

io.on('connection', (socket) => {
  console.log('User connected to Multiplayer:', socket.id);

  socket.on('user_join', (user: User) => {
    users[socket.id] = { ...user, id: socket.id };
    socket.broadcast.emit('user_joined', users[socket.id]);
    io.emit('users_update', users);
    console.log(`User ${user.name} joined the theater.`);
  });

  socket.on('update_position', (data: { position: [number, number, number], rotation: [number, number, number] }) => {
    if (users[socket.id]) {
      users[socket.id].position = data.position;
      users[socket.id].rotation = data.rotation;
      socket.broadcast.emit('user_moved', { id: socket.id, ...data });
    }
  });

  socket.on('disconnect', () => {
    if (users[socket.id]) {
      const name = users[socket.id].name;
      delete users[socket.id];
      io.emit('user_left', socket.id);
      io.emit('users_update', users);
      console.log(`User ${name} left the theater.`);
    }
  });
});

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log(`OSIN Multiplayer Server (v11) running on port ${PORT}`);
});
