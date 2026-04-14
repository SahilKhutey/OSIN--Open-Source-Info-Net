FROM node:20-slim

WORKDIR /app

COPY server/multiplayer-server/package*.json ./
RUN npm install

COPY server/multiplayer-server/server.ts ./

EXPOSE 4000

CMD ["npm", "start"]
