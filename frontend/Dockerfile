FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .
ARG REACT_APP_API_URL=http://localhost:8000/api/v1
ARG REACT_APP_GOOGLE_MAPS_KEY=
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_GOOGLE_MAPS_KEY=$REACT_APP_GOOGLE_MAPS_KEY

RUN CI=false npm run build

# Production stage — serve with nginx
FROM nginx:alpine AS production
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Development stage
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm ci
FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --silent
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
