# frontend/Dockerfile
FROM node:20-alpine
WORKDIR /usr/src/app

# Install deps
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Copy source
COPY . .

# Dev server
EXPOSE 5173
# Vite needs --host so it’s reachable from outside container
CMD ["npm", "run", "dev", "--", "--host"]
