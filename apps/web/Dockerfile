FROM node:22-bookworm-slim AS builder

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

# Copy workspace configuration
COPY package.json pnpm-workspace.yaml turbo.json ./
COPY pnpm-lock.yaml ./

# Copy web package definition
COPY apps/web/package.json ./apps/web/package.json

# Install workspace dependencies
RUN pnpm install --filter web... --frozen-lockfile

# Copy source
COPY apps/web ./apps/web

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ARG DATABASE_URL=postgresql://careeros:change_this_password@postgres:5432/careeros
ENV DATABASE_URL=$DATABASE_URL
ENV NEXT_TELEMETRY_DISABLED=1

# Build
RUN pnpm --filter web build


# -------------------------
# Production
# -------------------------

FROM node:22-bookworm-slim AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static

EXPOSE 3000

CMD ["node", "apps/web/server.js"]