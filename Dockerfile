# Build stage - build React app
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for frontend
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Copy built React app
COPY --from=builder /app/dist ./dist

# Copy server files
COPY --from=builder /app/server ./server

# Copy database files
COPY --from=builder /app/db ./db

# Install server dependencies
WORKDIR /app/server
RUN npm install --production

# Set environment
ENV NODE_ENV=production
ENV PORT=8080

# Expose port
EXPOSE 8080

# Start server
CMD ["node", "server.js"]
