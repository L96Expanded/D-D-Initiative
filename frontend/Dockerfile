FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

	# Install all dependencies (including dev)
	RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Use nginx to serve the built app
	# Remove dev dependencies for final image
	RUN npm prune --production
FROM nginx:alpine

# Copy built files to nginx
COPY --from=0 /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]