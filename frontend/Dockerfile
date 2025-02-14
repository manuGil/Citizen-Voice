FROM node:22.8.0-alpine3.20

# ARG API_URL

RUN mkdir -p /var/www/dockerize-nuxt/nuxt-app
WORKDIR /var/www/dockerize-nuxt/nuxt-app

RUN adduser --disabled-password nuxt
COPY package*.json ./
COPY . .
RUN rm yarn.lock
RUN chown -R nuxt:nuxt /var/www/dockerize-nuxt/nuxt-app
USER nuxt

# ENV API_PARTY_CMS_URL=${API_URL}

# RUN echo 'cms url at built: ' $API_PARTY_CMS_URL

RUN yarn install 

RUN yarn run build

EXPOSE 3000

CMD [ "yarn", "start" ]