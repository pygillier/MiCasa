FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Rewrites are baked at build time: the API is reachable as http://api:5000 inside compose.
ARG API_URL=http://api:5000
ENV API_URL=$API_URL
RUN npm run build

FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0 API_URL=http://api:5000
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
