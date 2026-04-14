FROM node:20-slim

WORKDIR /app

COPY server/xr-bridge/package*.json ./
RUN npm install

COPY server/xr-bridge/server.ts ./

# Build-time environment variables
ENV PORT=3001
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:29092

EXPOSE 3001

CMD ["npm", "start"]
