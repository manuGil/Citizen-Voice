FROM node:22.8.0-alpine3.20

RUN mkdir -p /var/www/dockerize-nuxt/nuxt-app
WORKDIR /var/www/dockerize-nuxt/nuxt-app


RUN adduser --disabled-password --no-create-home nuxt
COPY package*.json ./
COPY . .
RUN chown -R nuxt:nuxt /var/www/dockerize-nuxt/nuxt-app
USER nuxt

# RUN yarn install

# RUN yarn run build

# EXPOSE 3000

# ENV NUXT_HOST=0.0.0.0
# ENV NUXT_PORT=3000
# ENV API_PARTY_CMS_URL=http://localhost:3001

# CMD [ "yarn", "start" ]