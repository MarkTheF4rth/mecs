FROM node:lts-alpine

COPY package*.json ./

RUN npm install
RUN npm install @vue/cli-service-global
RUN npm install --save vue-google-charts

COPY . .
CMD ["sh", "start.sh"]
