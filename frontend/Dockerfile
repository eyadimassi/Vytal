# frontend/Dockerfile

# ---- Stage 1: Build the React App ----
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app's source code
COPY . .

# Build the app for production
RUN npm run build

# ---- Stage 2: Serve the App with Nginx ----
FROM nginx:1.23-alpine

# Copy the built static files from the 'build' stage
COPY --from=build /app/build /usr/share/nginx/html

# Nginx will automatically serve the index.html file from this directory
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]