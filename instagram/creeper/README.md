The Creeper
===

Server responsible for listening for Instagram posts, like a creep

# Setup

- Create credentials file (refer to `credentials.sh.template`)
- Source the credentials file: `source credentials.sh`
- Install dependencies: `npm install`
- Start up server: `npm run server`
- Subscribe to geo notifications: `sh scripts/subscribe.sh <hostname>`
- List geo notifications: `sh scripts/list.sh`
- After shutting down the server, make sure you unsubscribe: `sh scripts/unsubscribe`
