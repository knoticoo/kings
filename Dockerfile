# Use Node.js LTS version
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application files
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S canon-app -u 1001

# Change ownership of the app directory
RUN chown -R canon-app:nodejs /app
USER canon-app

# Expose port 6000
EXPOSE 6000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:6000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the application
CMD ["npm", "start"]