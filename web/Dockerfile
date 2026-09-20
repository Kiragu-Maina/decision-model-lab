FROM node:24-alpine AS dependencies
WORKDIR /workspace/web
COPY web/package.json web/package-lock.json ./
RUN npm ci

FROM node:24-alpine AS builder
WORKDIR /workspace/web
COPY --from=dependencies /workspace/web/node_modules ./node_modules
COPY web ./
RUN npm run build

FROM node:24-alpine AS runner
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0
WORKDIR /app
COPY --from=builder /workspace/web/.next/standalone ./
COPY --from=builder /workspace/web/.next/static ./.next/static
COPY --from=builder /workspace/web/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
