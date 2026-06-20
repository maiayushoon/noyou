# ─────────────────────────────────────────────────────────────────────────────
# NoYou dashboard — production image (multi-stage).
# Build context is the frontend/ directory:  docker build -t noyou-web ./frontend
#
# NEXT_PUBLIC_API_URL is inlined into the client bundle at BUILD time, so it must
# be supplied as a build arg (see docker-compose.yml / DEPLOY.md), not just at run.
# The app is served by `next start` (package.json "start" binds port 3001).
# ─────────────────────────────────────────────────────────────────────────────

# --- Stage 1: install dependencies (cached on package manifests) ---
FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# Use a clean, reproducible install when a lockfile is present; fall back to
# `npm install` for first-time builds before a lockfile is committed.
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# --- Stage 2: build the Next.js app ---
FROM node:20-slim AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} \
    NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# --- Stage 3: minimal runtime that runs `next start` ---
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3001

# Non-root runtime user.
RUN groupadd --gid 1001 nodejs \
    && useradd --uid 1001 --gid nodejs --create-home nextjs

# Copy only what `next start` needs to run the prebuilt app.
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.mjs ./next.config.mjs

USER nextjs
EXPOSE 3001

# `npm run start` => `next start -p 3001`.
CMD ["npm", "run", "start"]
