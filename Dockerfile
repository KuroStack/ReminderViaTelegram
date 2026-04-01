FROM php:8.3-cli

RUN apt-get update && apt-get install -y \
    git \
    curl \
    zip \
    unzip \
    sqlite3 \
    libsqlite3-dev \
    nodejs \
    npm \
    && docker-php-ext-install pdo pdo_sqlite \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /app

COPY composer.json composer.lock ./
RUN composer install --no-interaction --no-scripts --prefer-dist

COPY package.json ./
RUN npm install --ignore-scripts

COPY . .

RUN composer run-script post-autoload-dump || true && \
    npm run build && \
    cp .env.example .env && \
    php artisan key:generate && \
    touch database/database.sqlite && \
    php artisan migrate --force

EXPOSE 8000

CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]
