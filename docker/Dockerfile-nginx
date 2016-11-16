FROM nginx:1.11
MAINTAINER Open State Foundation <developers@openstate.eu>

RUN echo "Europe/Amsterdam" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

WORKDIR /usr/share/nginx/html

# Debug: use the nginx binary which was compiled with '--with-debug'
# CMD ["nginx-debug", "-g", "daemon off;"]
